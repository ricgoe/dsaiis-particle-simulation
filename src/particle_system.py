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
        self._interaction_matrix = self.convert_interaction_matrix(interaction_matrix)
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

    def convert_interaction_matrix(self, interaction_dict):
        """
        Konvertiert ein Dictionary {(1, 1): 1, (1, 2): -1, (2, 1): -1, (2, 2): 1}
        in eine NumPy-Matrix für schnelleren Zugriff mit numba.
        """
        max_type = max(max(k) for k in interaction_dict.keys())  # Größter Partikeltyp
        matrix = np.zeros((max_type + 1, max_type + 1), dtype=np.float64)

        for (i, j), value in interaction_dict.items():
            matrix[i, j] = value

        return matrix
    

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
        interaction_radius = 10*self.radius
        brwn_increment = np.random.normal(0, self.brownian_std, self.velocity.shape)
        self.velocity += brwn_increment

        max_speed = 10
        self.velocity = np.clip(self.velocity, -max_speed, max_speed)
        # update positions using current velocity
        new_positions = self._particles + self.velocity * self.delta_t
        new_positions = np.mod(new_positions, (self.width, self.height))
        # detect collisions with tentative new positions
        colliding_pairs = self.check_collisions(new_positions)
        # update velocities for each colliding pair
        update_collision_velocities_numba(new_positions, velocities=self.velocity, colliding_pairs=colliding_pairs, delta_t=self.delta_t, interaction_matrix=self.interaction_matrix, color_index=self._color_index, radius=self.radius, mode='collision')
        if interaction_radius:
            interaction_pairs = self.check_collisions(new_positions, radius=interaction_radius)
            update_collision_velocities_numba(new_positions, velocities=self.velocity, colliding_pairs=interaction_pairs, delta_t=self.delta_t, interaction_matrix=self.interaction_matrix, color_index=self._color_index, radius=self.radius, mode='interaction')
        
        self.velocity = np.nan_to_num(self.velocity)  # Ersetzt NaN/Inf durch 0

        # calc speeds of particles
        speeds = np.linalg.norm(self.velocity, axis=1, keepdims=True)
        # compute drag acceleration: -gamma (drag coefficient) * speed * velocity
        drag_acceleration = -self.drag * speeds * self.velocity*1
        self.velocity += drag_acceleration * self.delta_t
    
        final_positions = self._particles + self.velocity * self.delta_t
        self._particles = np.mod(final_positions, (self.width, self.height))


    
    def check_collisions(self, positions: np.ndarray, radius: float = None):
        """
        Wrapper für die numba-optimierte `check_collisions_numba`-Funktion.
        """
        if radius is None:
            radius = self.radius
        return check_collisions_numba(positions, radius)


           
    
    
  
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

@njit()
def calc_interaction_force_numba(distance, normal, interaction_strength, interaction_direction, equilibrium_distance, max_force=10):
    """
        Calculates the interaction force between particles based on interaction matrix
        not included in ParticleSystem anymore to use numba
        
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
    if distance > 0:
        force_magnitude = interaction_strength * (1 - np.exp(-abs(distance - equilibrium_distance))) * interaction_direction
    else:
        force_magnitude = max_force

    # numba does not support np.clip
    if force_magnitude > max_force:
        force_magnitude = max_force
    elif force_magnitude < -max_force:
        force_magnitude = -max_force

    return force_magnitude * normal


@njit()
def update_collision_velocities_numba(positions, velocities, colliding_pairs, delta_t, interaction_matrix, color_index, radius=None, mode="collision"):      
    """
    Updates velocities for each pair in colliding_pairs.
    not included in ParticleSystem, to use numba to speed it up
    
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
            v_rel = velocities[i] - velocities[j]
            sep_force = calc_repulsion_force_numba(distance, normal=normal, v_rel=v_rel, k=50, c=0.5, radius=radius)
            
            velocities[i] -= sep_force*delta_t # TODO: integrate mass 
            velocities[j] += sep_force*delta_t
    
        
        elif mode == 'interaction':
            type_i = color_index[i, 0]  # Partikeltyp von i
            type_j = color_index[j, 0]  # Partikeltyp von j
            interaction_direction = interaction_matrix[type_i, type_j]  # Jetzt korrekt!
            equilibrium_distance = 4 * radius
            interaction_force = calc_interaction_force_numba(distance, normal, interaction_strength=100, interaction_direction=interaction_direction, equilibrium_distance=equilibrium_distance)
            velocities[i] -= interaction_force * delta_t  # TODO: integrate mass
            velocities[j] += interaction_force * delta_t


@njit()
def calc_repulsion_force_numba(distance, normal, v_rel, k, c, radius):
    """
    Calculates repulsion force between two particles as in prevous version
    now with numba and not in class ParticleSystem
    """
    v_n = np.dot(v_rel, normal)
    delta = 2*radius-distance
    if delta > 0:
        force = (-k*delta-c*v_n)*normal
    
    return force



    
    
if __name__ == "__main__":
    part_sys = ParticleSystem(width=20, height=20, color_distribution=[((1, 0, 0, 1), 2), ((0, 1, 0, 1), 2)], radius=20, interaction_matrix={(1, 1): 1, (1, 2): -1, (2, 1): -1, (2, 2): 1})
    print(part_sys.particles)
    #part_sys.move_particles()
    
