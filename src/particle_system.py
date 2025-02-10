import numpy as np

class ParticleSystem:
    def __init__(self, width: int, height: int, color_distribution: list[tuple[tuple[int, int, int], int]], radius: int = 1, mass: int = 1, delta_t: float = 0.1, brownian_std: float = .05, drag: float = .01):
        self.color_distribution = color_distribution
        self.width: int = width
        self.height: int = height
        self.radius: int = radius
        self.mass: int = mass # not used for now
        self.delta_t: float = delta_t
        self.brownian_std: float = brownian_std
        self.drag: float = drag
        self._particles = self.init_particles()
        self.velocity = np.zeros((self._particles.shape[0], 2)) # x and y velocties
    
    @property
    def particles(self):
        return self._particles
    
    @particles.setter
    def particles(self, value):
        self._particles = value

    def init_particles(self):
        """
        Each particle row: [x, y, r, g, b, color_index]
        """
        part_arrays = []
        for color_index, (rgb, num_part) in enumerate(self.color_distribution):
            tmp_arr = np.random.uniform(0, self.width, size=(num_part, 2))
            rgb_arr = np.array(rgb)
            rgb_repeated = np.repeat(rgb_arr[None, :], repeats=num_part, axis=0)
            color_idx_column = np.full((num_part, 1), color_index)
            combined_arr = np.concatenate([tmp_arr, rgb_repeated, color_idx_column], axis=1)
            part_arrays.append(combined_arr)
        return np.concatenate(part_arrays, axis=0)
    
    
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

        brwn_increment = np.random.normal(0, self.brownian_std, self.velocity.shape)
        self.velocity += brwn_increment
        # update positions using current velocity
        new_positions = self._particles[:, :2] + self.velocity * self.delta_t
        new_positions = np.mod(new_positions, (self.width, self.height))
        # keep extra attributes (color distribution) in temp particle array
        temp_particles = np.hstack((new_positions, self._particles[:, 2:]))
        # detect collisions with tentative new positions
        colliding_pairs = self.check_collisions(temp_particles)
        # update velocities for each colliding pair
        self.update_collision_velocities(new_positions, colliding_pairs)
        self.velocity *= (1 - self.drag)
        final_positions = self._particles[:, :2] + self.velocity * self.delta_t
        final_positions = np.mod(final_positions, (self.width, self.height))
        self._particles = np.hstack((final_positions, self._particles[:, 2:])) 

        
        
    def check_collisions(self, particles_with_colors: np.ndarray, radius: float = None):
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
            
        positions = particles_with_colors[:, :2]  # get only x and y pos
        n = positions.shape[0]
        radius = self.radius

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
    
    def calc_seperation_force(self, distance: float, max_force: int) -> float:
        """
        Returns seperation force that is always smaller than 10. 
        The force gets scaled by the radius, so the values of the function at dist = 2r is always clipped at 10

        Args:
            distance (float): distance between two (colliding) particles

        Returns:
            force: force that is used to pull two particles apart along connection between center points
        """

        try:
            force = min(1/(distance/(max_force*2*self.radius)), max_force)
        except ZeroDivisionError:
            force = max_force
        return force
    
    def update_collision_velocities(self, positions: np.ndarray, colliding_pairs: list[tuple[int, int]]) -> None:
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

            # pull particles apart along normal
            sep_force = self.calc_seperation_force(distance, 10)
            self.velocity[i] += sep_force*normal
            self.velocity[j] -= sep_force*normal

    
if __name__ == "__main__":
    part_sys = ParticleSystem(width=20, height=20, color_distribution=[((1, 0, 0), 2), ((0, 1, 0), 2)], radius=20)
    part_sys.particles = np.array([[1, 1, 0, 1, 0], [1, 2, 0, 1, 0]])
    part_sys.move_particles()
