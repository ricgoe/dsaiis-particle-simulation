import numpy as np
from numba import njit

class ParticleSystem:
    def __init__(self, width: int, height: int, color_distribution: list[tuple[tuple[int, int, int, int], int]], radius: int = .5, mass: int = 0.5, restitution: float = .8, delta_t: float = 0.1, brownian_std: float = .1, drag: float = .1):
        self.color_distribution = color_distribution
        self.width: int = width
        self.height: int = height
        self.radius: int = radius
        self.mass: int = mass # not used for now
        self._delta_t: float = delta_t
        self.brownian_std: float = brownian_std
        self.drag: float = drag
        self._particles = None
        self._colors = None
        self._color_index = None
        self._particles, self._colors, self._color_index = self.init_particles()
        self._mass = np.full(self._particles.shape[0], mass)
        self._restitution = np.full(self._particles.shape[0], restitution)
        #self._interaction_matrix = interaction_matrix # positive values indicate attraction, negative values indicate repulsion
        self._velocity = np.zeros((self._particles.shape[0], 2)) # x and y velocties
        self._drag = drag
        
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
            for idx, (rgba, num) in enumerate(self.color_distribution, start=1)
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
    
    def move_particles(self):
        """
        Moves particles for one timestep and updates their velocities based on collision responses.
        The initial velocity is set only on the first call; subsequent calls use and update the current velocity.
        
        The method uses the current velocity to update particle positions, detects collisions, and then
        updates the velocity for each colliding pair by calling update_collision_positions.
        The particles’ positions are then updated with the modified velocity. This allows collision forces 
        (reflected in the velocity changes) to persist over time.
        
        Returns:
            Nones
        """

        self._velocity += np.random.normal(0, self.brownian_std, self._particles.shape)
        delta_pos = self._velocity*self._delta_t
        new_pos = np.mod(self._particles + delta_pos, (self.width, self.height))
        # detect collisions with tentative new positions
        colliding_pairs = self.check_collisions(new_pos) # sorted from left to right and bottom to top
        if not colliding_pairs:
            self._particles = new_pos # if there a re no collisions, just set the new position
            self._velocity *= (1 - self._drag)
            return
        increments = self.get_brwn_increment_from_involved_particles(colliding_pairs) # get the delta v's from the particles that are involved in the collision
        resulting_vector = np.sum(delta_pos[increments], axis=0) # calculate the resulting vector from the brwn increments
        if np.sum(resulting_vector) == 0: # if the resulting vector is zero, there is no movement
            return
        not_increments = np.delete(np.arange(len(self._particles)), increments, axis=0) # get the indices of the brwn increments that are not involved in the collision

        angle = int(self.angle_between(resulting_vector[0], resulting_vector[1])) # calculate the angle between the resulting vector and the positive x-axis
        if angle <= 90 or angle > 270:
            colliding_pairs.reverse() # if the angle is less than 90 or greater than 270, reverse the order of the colliding pairs
        self.update_collision_positions(new_pos, colliding_pairs, mode='collision') # update the positions using the colliding pairs
        self._particles[not_increments] = new_pos[not_increments] # update the positions of the particles that are not involved in the collision
        new_pos = self._particles.copy()


    def get_brwn_increment_from_involved_particles(self, colling_pairs: list[tuple[int]]) -> np.ndarray:
        # returns all the brwn increments that are involved in the collision to calculate a resulting vector from all brwn increments
        return list({num for pair in colling_pairs for num in pair})
        

           
    def check_collisions(self, positions: np.ndarray, radius: float = None):
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

        # check candidates for collisions, because overlap of bounding boxes is not enough
        colliding_pairs = []
        for i, j in candidate_pairs:
            dx = positions[i, 0] - positions[j, 0]
            dy = positions[i, 1] - positions[j, 1]
            distance_sq = dx**2 + dy**2
            if distance_sq <= (2 * radius)**2:
                colliding_pairs.append((i, j))
                
            # print(f"Colliding pair: {i}, {j}")

        return colliding_pairs
            
    

    def update_collision_positions(self, positions: np.ndarray, colliding_pairs: list[tuple[int, int]], mode: str = "collsion", interaction_radius: float = None, **kwargs) -> np.ndarray:
        """
        Updates velocities for each pair in colliding_pairs.
        
        Parameters:
            positions (np.ndarray): Current positions of particles.
            colliding_pairs (list of tuple): List of index pairs.

        Returns:
            None
        """
        
        for i, j in colliding_pairs:
            # calculate vector between particle centers
            dx = positions[i, 0] - positions[j, 0]
            dy = positions[i, 1] - positions[j, 1]
            distance = np.sqrt(dx**2 + dy**2)
            if distance == 0:
                # avoid division by zero: assign random normalized vector
                normal = np.random.uniform(-1, 1, size=2)
                normal /= np.linalg.norm(normal)
            else:
                normal = np.array([dx, dy]) / distance

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
                
                #self._particles[i] = self.move_position(positions[i], self._velocity[i]*self._delta_t)
                #self._particles[j] = self.move_position(positions[j], self._velocity[j]*self._delta_t)
                
                
                            



    
if __name__ == "__main__":
    part_sys = ParticleSystem(width=20, height=20, color_distribution=[((1, 0, 0, 1), 2), ((0, 1, 0, 1), 2)], radius=20, interaction_matrix={(1, 1): 1, (1, 2): -1, (2, 1): -1, (2, 2): 1})
    print(part_sys.particles)
    #part_sys.move_particles()
    
