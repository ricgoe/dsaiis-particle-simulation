import numpy as np
import time


class ParticleSystem:
    def __init__(self, width: int, height: int, color_distribution: list[tuple[tuple[int, int, int, int], int]], interaction_matrix: dict[tuple[int, int], float], radius: int = .5, mass: int = 0.5, restitution: float = 1, delta_t: float = 0.3, brownian_std: float = .05, drag: float = 0.5, min_vel: float = -1, max_vel: float = 1):
        self._particles = None
        self._colors = None
        self._color_index = None
        self.width: int = width
        self.height: int = height
        self.radius: int = radius
        self._delta_t: float = delta_t
        self.brownian_std: float = brownian_std
        self._drag = drag
        self._color_distribution = color_distribution
        self._particles, self._colors, self._color_index = self.init_particles()
        # self._velocity = np.zeros((self._particles.shape[0], 2)) # x and y velocties
        speeds = np.random.uniform(min_vel, max_vel, self._particles.shape[0])
        angles = np.random.uniform(0, 2 * np.pi, self._particles.shape[0])
        self._velocity = np.column_stack((speeds * np.cos(angles), speeds * np.sin(angles)))
        self._mass = np.full(self._particles.shape[0], mass)
        self._restitution = np.full(self._particles.shape[0], restitution)
        self._interaction_matrix = interaction_matrix # positive values indicate attraction, negative values indicate repulsion
        #self._velocity = np.array([[1.2, 1.2], [-.7, 1]], dtype=float)
    
    
    @property
    def particles(self):
        return self._particles
    
    @property
    def positions(self):
        return self._particles
    
    @property
    def colors(self):
        return self._colors
    
    @property
    def size(self):
        return np.full(self._particles.shape[0], self.radius)
    
    @property
    def interaction_matrix(self):
        return self._interaction_matrix
    
    @property
    def delta_t(self):
        return self._delta_t
    
    @particles.setter
    def particles(self, value):
        self._particles = value
    
    @interaction_matrix.setter
    def interaction_matrix(self, value):
        self._interaction_matrix = value
        
    @delta_t.setter
    def delta_t(self, value):
        self._delta_t = value
        
    

    def init_particles(self):
        """
        Each particle row: [x, y]
        Each color row: [r, g, b, a]
        
        """
        particles = [
            (
                np.random.uniform(0, self.width, size=(num, 2)), 
                np.tile(np.array(rgba), (num, 1)), 
                np.full((num, 1), idx)
            ) 
            for idx, (rgba, num) in enumerate(self._color_distribution, start=1)
        ]
        positions, colors, color_indices = map(lambda arrays: np.concatenate(arrays, axis=0), zip(*particles))
    
        return positions, colors, color_indices
    
    
    def move_position(self, position: np.ndarray, amout: np.ndarray) -> np.ndarray:
        return position + amout
    
    
    def angle_between(self, x, y):
        # Compute the angle in radians between the positive x-axis and [x, y]
        angle_rad = np.arctan2(y, x)
        # Convert to degrees and adjust to [0, 360)
        angle_deg = np.degrees(angle_rad) % 360
        return angle_deg
    

    def move_particles(self, skip_interaction: bool = False):
        """
        Moves particles for one timestep and updates their velocities based on collision responses.
        The initial velocity is set only on the first call; subsequent calls use and update the current velocity.
        
        The method uses the current velocity to update particle positions, detects collisions, and then
        updates the velocity for each colliding pair by calling update_velocities_collisions.
        The particles’ positions are then updated with the modified velocity. This allows collision forces 
        (reflected in the velocity changes) to persist over time.
        
        Returns:
            Nones
        """
        #start = time.time()
        interaction_radius = 0
        speeds = np.linalg.norm(self._velocity, axis=1)
        nonzero = speeds > 0  # avoid division by zero
        if np.any(nonzero):
            # Compute current angles for particles with nonzero speed.
            current_angles = np.arctan2(self._velocity[nonzero, 1], self._velocity[nonzero, 0])
            # Determine a small random rotation (in radians) for each particle.
            delta_angles = np.random.normal(0, self.brownian_std, size=current_angles.shape)
            new_angles = current_angles + delta_angles
            # Update velocities while preserving their speeds.
            self._velocity[nonzero, 0] = speeds[nonzero] * np.cos(new_angles)
            self._velocity[nonzero, 1] = speeds[nonzero] * np.sin(new_angles)
        else:
            # Optionally, if any particles are at rest, initialize them with a default speed.
            initial_speed = 1.0  # adjust as needed
            angles = np.random.uniform(0, 2*np.pi, size=self._velocity.shape[0])
            self._velocity[:, 0] = initial_speed * np.cos(angles)
            self._velocity[:, 1] = initial_speed * np.sin(angles)
        delta_pos = self._velocity*self._delta_t
        new_pos = np.mod(self._particles + delta_pos, (self.width, self.height))
        # detect collisions with tentative new positions
        colliding_pairs = self.check_collisions(new_pos) # sorted from left to right and bottom to top
        if not colliding_pairs:
            self._particles = new_pos # if there are no collisions, just set the new position
            #self._velocity *= (1 - self._drag)
            return
        increments = self.get_brwn_increment_from_involved_particles(colliding_pairs) # get the delta v's from the particles that are involved in the collision
        resulting_vector = np.sum(delta_pos[increments], axis=0) # calculate the resulting vector from the brwn increments
        if np.sum(resulting_vector) == 0: # if the resulting vector is zero, there is no movement
            return
        angle = int(self.angle_between(resulting_vector[0], resulting_vector[1])) # calculate the angle between the resulting vector and the positive x-axis
        if angle <= 90 or angle > 270:
            colliding_pairs.reverse() # if the angle is less than 90 or greater than 270, reverse the order of the colliding pairs
        
        self.update_velocities_collisions(new_pos, colliding_pairs, mode='collision') # update the velocities using the colliding pairs
        if interaction_radius and not skip_interaction:
            interaction_pairs = self.check_collisions(new_pos, radius=interaction_radius, mode = 'interaction')
            self.update_velocities_collisions(new_pos, interaction_pairs, mode='interaction', interaction_radius=interaction_radius)
        # calc speeds of particles
        #self._velocity *= (1-self._drag)
        #end = time.time()
        #print(f"Time taken for collisions: {end - start}")
        #self.calculate_drag()

    def calculate_drag(self):
        drag = 0.5*self._velocity**2
        self._velocity *= (1-(0.5*drag)**2)
        

    def get_brwn_increment_from_involved_particles(self, colling_pairs: list[tuple[tuple[int], float, np.ndarray]]) -> np.ndarray:
        # returns all the brwn increments that are involved in the collision to calculate a resulting vector from all brwn increments
        return list({num for pair, distance, normal in colling_pairs for num in pair})
        

    def check_collisions(self, positions: np.ndarray, radius: float = None, mode = 'collision'):
        """
        Detects colliding pairs using a sweep and prune approach.
        
        Parameters:
            particles_with_colors (np.ndarray): Array with particle info (positions in the first two columns).
            radius (float): The effective radius to use for collision checking.
                            Defaults to self.radius if not provided.

        Returns:
            list[tuple[int, int]]: each tuple contains the indices of two colliding particles.
        """
        
        if radius is None:
            radius = self.radius
            
        n = positions.shape[0]

        # compute bounding boxes for each particle for x and y axis
        x_intervals = [(positions[i, 0] - radius, positions[i, 0] + radius, i) for i in range(n)]
        y_intervals = [(positions[i, 1] - radius, positions[i, 1] + radius) for i in range(n)]
        
        # create events for sweep (0 for start, 1 for end)
        events = []
        for (x_min, x_max, idx) in x_intervals:
            events.append((x_min, 0, idx))  # start event
            events.append((x_max, 1, idx))  # end event

        # sort events by x coordinate; if equal, start events come first
        events.sort(key=lambda e: (e[0], e[1]))

        active = []  # active means particles that end event didnt happen yet
        candidate_pairs = []

        for pos, event_type, idx in events:
            if event_type == 0:  # check against all active particles
                for other in active:
                    # check for overlap along the y-axis
                    y_min_i, y_max_i = y_intervals[idx]
                    y_min_j, y_max_j = y_intervals[other]
                    if y_max_i >= y_min_j and y_max_j >= y_min_i:
                        candidate_pairs.append((idx, other))
                active.append(idx)
            else:  # remove particle from active list if end event happened
                active.remove(idx)
        
        # if mode != 'collision':
        #     return candidate_pairs
        # check candidates for collisions, because overlap of bounding boxes is not enough
        colliding_pairs = []
        for i, j in candidate_pairs:
            dx = positions[i, 0] - positions[j, 0]
            dy = positions[i, 1] - positions[j, 1]
            distance = np.sqrt(dx**2 + dy**2)
            if distance <= 2 * radius:
                normal = np.array([dx, dy]) / distance
                colliding_pairs.append(((i, j), distance, normal))
                
            # print(f"Colliding pair: {i}, {j}")

        return colliding_pairs
            
    
    def update_velocities_collisions(self, positions: np.ndarray, colliding_pairs: list[tuple[int, int]], mode: str = "collision", interaction_radius: float = None, **kwargs) -> np.ndarray:
        """
        Updates velocities for each pair in colliding_pairs.
        
        Parameters:
            positions (np.ndarray): Current positions of particles.
            colliding_pairs (list of tuple): List of index pairs.

        Returns:
            None
        """
        for ((i, j), distance, normal) in colliding_pairs:
            if mode == 'collision':
                depth = 2*self.radius - distance
                self._particles[i] = self.move_position(positions[i], depth*normal*0.5)
                self._particles[j] = self.move_position(positions[j], -depth*normal*0.5)
                
                v_rel = self._velocity[j] - self._velocity[i]
                # e = np.min(self._restitution[i], self._restitution[j]) # resitution factor
                e = self._restitution[i] # resitution factor
                factor_j = -(1+e)*np.dot(v_rel, normal)
                factor_j /= (1/self._mass[i]) + (1/self._mass[j])
                self._velocity[i] -= factor_j / self._mass[i] * normal
                self._velocity[j] += factor_j / self._mass[j] * normal
            
            elif mode == 'interaction':
                pass
                # # interaction matrix always
                # interaction_magnitude = self._interaction_matrix[(self._color_index[min(i,j), 0], self._color_index[max(i,j), 0])]
                # #equilibrium_distance = 2 * self.radius
                # interaction_force = (1/dist)*normal #self.calc_interaction_force(distance, normal, interaction_strength=100, interaction_direction=interaction_direction, equilibrium_distance=equilibrium_distance)
                # self._velocity[i] -= interaction_force * self.delta_t  # TODO: integrate mass
                # self._velocity[j] += interaction_force * self.delta_t

                
    def calc_interaction_force(self, distance: float, normal: np.ndarray, interaction_strength: float, interaction_direction: float, equilibrium_distance: float, max_force: float = 20) -> np.ndarray:
        """
        Calculates the interaction force between particles based on interaction matrix
        
        Parameters:
            distance (float): Distance between two particles.
            normal (np.ndarray): Normalized direction vector between particles.
            interaction_strength (float): Strength of interaction from interaction_matrix.
            interaction_type (float): Positive for attraction, negative for repulsion.
            equilibrium_distance (float): Preferred distance for stable interactions.
            max_force (float): Maximum force limit.

        Returns:
            np.ndarray: Force vector applied to the particles.
        """
        
        # stronger at short distances, weaker at long distances
        if distance > 0:
            force_magnitude = 1/distance**2#interaction_strength * (1 - np.exp(-abs(distance - equilibrium_distance))) * interaction_direction
        else:
            force_magnitude = max_force

        # prevent excessive attraction/repulsion
        force_magnitude = np.clip(force_magnitude, -max_force, max_force)
        return 15 * normal        
                            



    
if __name__ == "__main__":
    part_sys = ParticleSystem(width=1000, height=1000, color_distribution=[((1, 0, 0, 1), 2), ((0, 1, 0, 1), 2)], radius=20, interaction_matrix={(1, 1): 1, (1, 2): -1, (2, 1): -1, (2, 2): 1})

    
