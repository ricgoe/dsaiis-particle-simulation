import numpy as np
from numba import njit

class ParticleSystem:
    def __init__(self, width: int, height: int, color_distribution: list[tuple[tuple[int, int, int, int], int]], interaction_matrix:dict[tuple:int], radius: int = 5, mass: int = 1, delta_t: float = 0.1, brownian_std: float = .3, drag: float = .1):
        self.color_distribution = color_distribution
        self.width: int = width
        self.height: int = height
        self.radius: int = radius
        self.mass: int = mass # not used for now
        self.delta_t: float = delta_t
        self.brownian_std: float = brownian_std
        self.drag: float = drag
        self._particles, self._colors, self._color_index = self.init_particles()
        self._interaction_matrix = interaction_matrix # positive values indicate attraction, negative values indicate repulsion
        self.velocity = np.zeros((self._particles.shape[0], 2)) # x and y velocties
        check_collisions_numba(np.array([[0.0, 0.0], [1.0, 1.0]]), self.radius)
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
    
    @particles.setter
    def particles(self, value):
        self._particles = value
    
    @interaction_matrix.setter
    def interaction_matrix(self, value):
        self._interaction_matrix = value
    

    def init_particles(self):
        """
        Each particle row: [x, y, color_index]
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
    
    
    def move_particles(self):
        """
        Moves particles for one timestep and updates their velocities based on collision responses.
        The initial velocity is set only on the first call; subsequent calls use and update the current velocity.
        
        The method uses the current velocity to update particle positions, detects collisions, and then
        updates the velocity for each colliding pair by calling update_collision_velocities.
        The particles’ positions are then updated with the modified velocity. This allows collision forces 
        (reflected in the velocity changes) to persist over time.
        
        Returns:
            None
        """
        interaction_radius = 5*self.radius
        brwn_increment = np.random.normal(0, self.brownian_std, self.velocity.shape)
        self.velocity += brwn_increment
        # update positions using current velocity
        new_positions = self._particles + self.velocity * self.delta_t
        new_positions = np.mod(new_positions, (self.width, self.height))
        # detect collisions with tentative new positions
        colliding_pairs = self.check_collisions2(new_positions)
        # update velocities for each colliding pair
        self.update_collision_velocities(new_positions, colliding_pairs, mode='collision')
        if interaction_radius:
            interaction_pairs = self.check_collisions2(new_positions, radius=interaction_radius)
            self.update_collision_velocities(new_positions, interaction_pairs, mode='interaction', interaction_radius=interaction_radius)
        
        # calc speeds of particles
        speeds = np.linalg.norm(self.velocity, axis=1, keepdims=True)
        # compute drag acceleration: -gamma (drag coefficient) * speed * velocity
        drag_acceleration = -self.drag * speeds * self.velocity*1
        self.velocity += drag_acceleration * self.delta_t
        final_positions = self._particles + self.velocity * self.delta_t
        self._particles = np.mod(final_positions, (self.width, self.height))

    
    def check_collisions2(self, positions: np.ndarray, radius: float = None):
        """
        Wrapper für die numba-optimierte `check_collisions_numba`-Funktion.
        """
        if radius is None:
            radius = self.radius
        return check_collisions_numba(positions, radius)


           
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
    
    
    def calc_seperation_force(self, distance: float, max_force: int, normal, radius: float = None) -> float:
        """
        Returns seperation force that is always smaller than 10. 
        The force gets scaled by the radius, so the values of the function at dist = 2r is always clipped at 10

        Args:
            distance (float): distance between two (colliding) particles

        Returns:
            force: force that is used to pull two particles apart along connection between center points
        """
        if radius is None:
            radius = self.radius
        
        try:
            force = min(1/(distance/(max_force*2*radius)), max_force)
        except ZeroDivisionError:
            force = max_force
        return -force * normal
    
    def calc_repulsion_force(self, distance: float, normal: float, v_rel: float, k: float, c: float = .5) -> float:
        v_n = np.dot(v_rel, normal)
        delta = 2*self.radius-distance
        if delta > 0:
            force = (-k*delta-c*v_n)*normal
        
        return force
    
    def calc_interaction_force(self, distance: float, normal: np.ndarray, interaction_strength: float, interaction_direction: float, equilibrium_distance: float, max_force: float = 10) -> np.ndarray:
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
            force_magnitude = interaction_strength * (1 - np.exp(-abs(distance - equilibrium_distance))) * interaction_direction
        else:
            force_magnitude = max_force

        # prevent excessive attraction/repulsion
        force_magnitude = np.clip(force_magnitude, -max_force, max_force)
        return force_magnitude * normal
    
    
    
    
    def update_collision_velocities(self, positions: np.ndarray, colliding_pairs: list[tuple[int, int]], mode: str = "collsion", interaction_radius: float = None, **kwargs) -> None:
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
                # pull particles apart along normal<
                #sep_force = self.calc_seperation_force(distance, 80)
                v_rel = self.velocity[i] - self.velocity[j]
                sep_force = self.calc_repulsion_force(distance, normal=normal, v_rel=v_rel, k=50, c=0.5)
                
                self.velocity[i] -= sep_force*self.delta_t # TODO: integrate mass 
                self.velocity[j] += sep_force*self.delta_t
            
            # elif mode == 'interaction':
            #     sep_force = self.calc_seperation_force(distance, 20, interaction_radius)
            #     interaction_direction = self.interaction_matrix[int(self._particles[i, -1]), int(self._particles[j, -1])]
            #     self.velocity[i] -= interaction_direction*sep_force*normal*self.delta_t # TODO: integrate mass 
            #     self.velocity[j] += interaction_direction*sep_force*normal*self.delta_t
            
            elif mode == 'interaction':
                interaction_direction = self.interaction_matrix[(self._color_index[i, 0], self._color_index[j, 0])]
                equilibrium_distance = 4 * self.radius
                interaction_force = self.calc_interaction_force(distance, normal, interaction_strength=100, interaction_direction=interaction_direction, equilibrium_distance=equilibrium_distance)
                self.velocity[i] -= interaction_force * self.delta_t  # TODO: integrate mass
                self.velocity[j] += interaction_force * self.delta_t
                
    def calculate_resistance_force(self, velocity: np.ndarray) -> np.ndarray:
        return 0.5*(velocity**2)
    
@njit()
def check_collisions_numba(positions, radius):
    """
    Sweep & Prune algorithm for collision detection.
    not included in ParticleSystem, to use numba to speed it up
    
    Parameters:
        positions (np.ndarray): array with particle positions x,y 
        radius (float): radius to use for collision detection/ interaction

    Returns:
        np.ndarray: array with indices of colliding particles.
    """
    n = positions.shape[0]
    radius_sq = (2 * radius) ** 2  # to avoid sqrt

    # sort particles by x coordinate, int32 for faster indexing
    x_sorted_indices = np.argsort(positions[:, 0]).astype(np.int32)
    x_sorted = positions[x_sorted_indices]

    candidate_pairs = []
    for i in range(n):
        x_i = x_sorted[i, 0]
        y_i = x_sorted[i, 1]
        
        # search for all particles to the right
        for j in range(i + 1, n):
            x_j = x_sorted[j, 0]
            y_j = x_sorted[j, 1]

            # stop if the particles are too far apart along the x-axis
            # every other particle is guaranteed to be too far away along the x-axis
            # x_j - x_i is also guaranteed to be positive or zero
            if x_j - x_i > 2 * radius:
                break

            # calculate distance to the other particle
            dx = x_j - x_i
            dy = y_j - y_i
            dist_sq = dx * dx + dy * dy

            # check if the particles are within the defined radius
            if dist_sq <= radius_sq:
                candidate_pairs.append((x_sorted_indices[i], x_sorted_indices[j]))

    return np.array(candidate_pairs, dtype=np.int32)



    
if __name__ == "__main__":
    part_sys = ParticleSystem(width=20, height=20, color_distribution=[((1, 0, 0, 1), 2), ((0, 1, 0, 1), 2)], radius=20, interaction_matrix={(1, 1): 1, (1, 2): -1, (2, 1): -1, (2, 2): 1})
    print(part_sys.particles)
    #part_sys.move_particles()
    
