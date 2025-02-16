import numpy as np
from scipy.spatial import cKDTree
from IntegrityChecks import _validate_particle_entry

class ParticleSystem:
    def __init__(self, width: int, height: int, color_distribution: list[tuple[tuple[int, int, int, int], int, int, int]], interaction_matrix: dict[tuple[int, int], float], radius: int = .5, delta_t: float = 0.3, brownian_std: float = .01, drag: float = 0.5, min_vel: float = -5, max_vel: float = 5):
        """
        Initializes a new ParticleSystem instance with specified simulation parameters.
        
        Parameters
        ----------
        width : int
            The width of the simulation area.
        height : int
            The height of the simulation area.
        color_distribution : list[tuple[tuple[int, int, int, int], int, int, int]]
            List of tuples defining the particle classes. Each tuple contains:
            - A tuple (r, g, b, a) representing the color.
            - An integer representing the number of particles.
            - An integer representing the restitution coefficient.
            - An integer representing the mass.
        interaction_matrix : dict[tuple[int, int], float]
            Dictionary mapping a pair of particle class indices to their interaction magnitude.
            Positive values indicate attraction, negative values indicate repulsion.
        radius : int, optional
            The radius of each particle (default is 0.5).
        delta_t : float, optional
            The time step for particle movement (default is 0.3).
        brownian_std : float, optional
            Standard deviation for random Brownian motion in particle angles (default is 0.01).
        min_vel : float, optional
            Minimum initial velocity magnitude (default is -5).
        max_vel : float, optional
            Maximum initial velocity magnitude (default is 5).
        """
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
        self._particles, self._colors, self._color_index, self._restitution, self._mass = self.init_particles()
        speeds = np.random.uniform(min_vel, max_vel, self._particles.shape[0])
        angles = np.random.uniform(0, 2 * np.pi, self._particles.shape[0])
        self._velocity = np.column_stack((speeds * np.cos(angles), speeds * np.sin(angles)))
        self._interaction_matrix = interaction_matrix # positive values indicate attraction, negative values indicate repulsion
    
    
    @property
    def positions(self):
        """
        Retrieves the current particle positions.
        
        Returns
        -------
        np.ndarray
            A 2D array of shape (N, 2) containing the (x, y) positions of the particles.
        """
        return self._particles
    
    @property
    def colors(self):
        """
        Retrieves the colors of the particles.
        
        Returns
        -------
        np.ndarray
            A 2D array of shape (N, 4) containing the RGBA colors of the particles.
        """
        return self._colors
    
    @property
    def size(self):
        """
        Retrieves the size (radius) of each particle.
        
        Returns
        -------
        np.ndarray
            A 1D array filled with the particle radius for each particle.
        """
        return np.full(self._particles.shape[0], self.radius)
    
    @property
    def interaction_matrix(self):
        """
        Retrieves the interaction matrix between particle classes.
        
        Returns
        -------
        dict[tuple[int, int], float]
            Dictionary mapping particle class pairs to their interaction magnitudes.
        """
        return self._interaction_matrix
    
    @property
    def delta_t(self):
        """
        Retrieves the current time step used for particle movement.
        
        Returns
        -------
        float
            The time step delta.
        """
        return self._delta_t
    
    @positions.setter
    def positions(self, value):
        """
        Sets new particle positions.
        
        Parameters
        ----------
        value : np.ndarray
            A 2D array of new particle positions.
        """
        self._positions = value
    
    @interaction_matrix.setter
    def interaction_matrix(self, value):
        """
        Sets a new interaction matrix.
        
        Parameters
        ----------
        value : dict[tuple[int, int], float]
            New dictionary mapping particle class pairs to interaction magnitudes.
        """
        self._interaction_matrix = value
        
    @delta_t.setter
    def delta_t(self, value):
        """
        Sets a new time step for particle movement.
        
        Parameters
        ----------
        value : float
            The new time step delta.
        """
        self._delta_t = value
        
    

    def init_particles(self):
        """
        Initializes particles with random positions and assigns colors, restitution, and mass.
        
        Returns
        -------
        positions : np.ndarray
            A 2D array of shape (N, 2) containing the (x, y) positions of the particles.
        colors : np.ndarray
            A 2D array of shape (N, 4) containing the RGBA colors of the particles.
        color_indices : np.ndarray
            A 2D array of shape (N, 1) containing the class index for each particle.
        restitution : np.ndarray
            A 1D array of restitution coefficients for the particles.
        mass : np.ndarray
            A 1D array of masses for the particles.
        """
        
        particles = []
        for idx, (rgba, num, restitution, mass) in enumerate(self._color_distribution, start=1):
            _validate_particle_entry(rgba, num, restitution, mass)
            x_coords = np.random.uniform(0, self.width, size=num)
            y_coords = np.random.uniform(0, self.height, size=num)
            positions = np.column_stack((x_coords, y_coords))
            colors = np.tile(np.array(rgba), (num, 1))
            color_indices = np.full((num, 1), idx)
            restitutions = np.full((num,), restitution)
            masses = np.full((num,), mass)
            particles.append((positions, colors, color_indices, restitutions, masses))
            
        positions, colors, color_indices, restitution, mass = map(lambda arrays: np.concatenate(arrays, axis=0), zip(*particles))
    
        return positions, colors, color_indices, restitution, mass


    def move_particles(self, skip_interaction: bool = False):
        """
        Moves particles for one time step and updates their velocities based on collisions and interactions.
        
        Parameters
        ----------
        skip_interaction : bool, optional
            If True, skips updating interactions between particles (default is False).
        
        Returns
        -------
        None
        """
        interaction_radius = 10*self.radius
        speeds = np.linalg.norm(self._velocity, axis=1)
        nonzero = speeds > 0
        if np.any(nonzero):
            # compute current angles for particles
            current_angles = np.arctan2(self._velocity[nonzero, 1], self._velocity[nonzero, 0])
            # determine small random rotation
            delta_angles = np.random.normal(0, self.brownian_std, size=current_angles.shape)
            new_angles = current_angles + delta_angles
            self._velocity[nonzero, 0] = speeds[nonzero] * np.cos(new_angles)
            self._velocity[nonzero, 1] = speeds[nonzero] * np.sin(new_angles)
        else:
            # if any particles are at rest, initialize with default speed
            initial_speed = 1.0
            angles = np.random.uniform(0, 2*np.pi, size=self._velocity.shape[0])
            self._velocity[:, 0] = initial_speed * np.cos(angles)
            self._velocity[:, 1] = initial_speed * np.sin(angles)
        delta_pos = self._velocity*self._delta_t
        new_pos = self._wrap_around(self._particles + delta_pos)
        # detect collisions with tentative new positions
        collision_data = self.check_collisions(new_pos, radius=self.radius) # sorted from left to right and bottom to top
        if collision_data[0].size == 0:
            self._particles = new_pos
            return
        
        self.update_velocities_collisions(new_pos, collision_data, mode='collision')
        # For interaction mode, assuming check_collisions returns candidate pairs when mode != 'collision'
        if interaction_radius and not skip_interaction:
            interaction_candidates = self.check_collisions(new_pos, radius=interaction_radius)
            self.update_velocities_collisions(new_pos, interaction_candidates, mode='interaction')
    
    
    def check_collisions(self, positions: np.ndarray, radius: float) -> tuple:
        """
        Detects collisions between particles using a spatial tree.
        
        Parameters
        ----------
        positions : np.ndarray
            A 2D array of particle positions.
        radius : float
            The effective radius used for collision detection.
        
        Returns
        -------
        tuple
            A tuple containing:
            - i_idx : np.ndarray of indices for the first particle in each colliding pair.
            - j_idx : np.ndarray of indices for the second particle.
            - distances : np.ndarray of distances between colliding particles.
            - normals : np.ndarray of unit vectors pointing from the second particle to the first.
        """
        # boxsize=[self.width, self.height] is necessary for periodic boundaries
        tree = cKDTree(positions, boxsize=[self.width, self.height])
        pairs = tree.query_pairs(r=2*radius)
        
        if not pairs:
            return (np.empty(0, dtype=int),
                    np.empty(0, dtype=int),
                    np.empty(0),
                    np.empty((0, 2)))
        
        pairs_arr = np.array(list(pairs), dtype=int)  # shape (M, 2)
        i_idx = pairs_arr[:, 0]
        j_idx = pairs_arr[:, 1]
        
        # compute differences, wrap around boundaries
        dx = (positions[i_idx, 0] - positions[j_idx, 0] + self.width/2) % self.width - self.width/2
        dy = (positions[i_idx, 1] - positions[j_idx, 1] + self.height/2) % self.height - self.height/2
        distances = np.sqrt(dx**2 + dy**2)
        
        normals = np.column_stack((dx, dy))
        distances_safe = np.where(distances == 0, 1, distances)
        normals /= distances_safe[:, None]
        
        return i_idx, j_idx, distances, normals
    
     
    def update_velocities_collisions(self, positions: np.ndarray, colliding_data, mode: str = "collision") -> None:
        """
        Updates particle velocities (and positions) based on collisions or interactions.
        
        Parameters
        ----------
        positions : np.ndarray
            The current particle positions.
        colliding_data : tuple
            A tuple containing indices, distances, and normals of colliding or interacting particles.
        mode : str, optional
            The update mode:
            - "collision": Handle physical collisions by adjusting positions and velocities.
            - "interaction": Update velocities based on interactions between particles.
            (default is "collision").
        
        Returns
        -------
        None
        """
        if mode == "collision":
            i_idx, j_idx, distances, normals = colliding_data
            # calculate overlap (depth) for each collision
            depth = 2 * self.radius - distances
            self._particles[i_idx] = positions[i_idx] + 0.5 * depth[:, None] * normals
            self._particles[j_idx] = positions[j_idx] - 0.5 * depth[:, None] * normals
            # calculate the relative velocity for each colliding pair
            v_rel = self._velocity[j_idx] - self._velocity[i_idx]
            # minimum restitution
            e = np.minimum(self._restitution[i_idx], self._restitution[j_idx])
            # compute the component of the relative velocity along the collision normal
            dot = np.sum(v_rel * normals, axis=1)
            # compute impulse magnitude for each collision pair
            factor = -(1 + e) * dot
            denom = (1 / self._mass[i_idx]) + (1 / self._mass[j_idx])
            factor /= denom  # shape (K,)
            
            self._velocity[i_idx] -= (factor / self._mass[i_idx])[:, None] * normals
            self._velocity[j_idx] += (factor / self._mass[j_idx])[:, None] * normals
            
        elif mode == 'interaction':
            # array of candidate pairs (n, 2)
            i_idx, j_idx, distances, normals = colliding_data
            if i_idx.size == 0:
                return

            # compute vector from particle j to particle i
            direction = self._particles[i_idx] - self._particles[j_idx]  # shape (n, 2)
            norms = np.linalg.norm(direction, axis=1)  # shape (n,)

            valid = norms > 0
            if not np.any(valid):
                return 

            valid_i = i_idx[valid]
            valid_j = j_idx[valid]
            direction_valid = direction[valid]
            norms_valid = norms[valid]
            normals = direction_valid / norms_valid[:, None]

            # compute desired angles from the normals
            desired_angles = np.arctan2(normals[:, 1], normals[:, 0])

            colors_i = self._color_index[valid_i, 0]
            colors_j = self._color_index[valid_j, 0]
            min_colors = np.minimum(colors_i, colors_j)
            max_colors = np.maximum(colors_i, colors_j)
            lookup = np.vectorize(lambda a, b: self._interaction_matrix[(a, b)])
            interaction_magnitudes = lookup(min_colors, max_colors)

            # repulsive interactions, adjust desired angle by π
            repulsive = interaction_magnitudes < 0
            desired_angles[repulsive] = (desired_angles[repulsive] + np.pi) % (2 * np.pi)

            # get current angles of velocities for particles i and j
            current_angles_i = np.arctan2(self._velocity[valid_i, 1], self._velocity[valid_i, 0])
            current_angles_j = np.arctan2(self._velocity[valid_j, 1], self._velocity[valid_j, 0])

            alpha = np.where(interaction_magnitudes > 0,
                            0.05 * np.abs(interaction_magnitudes),
                            0.1 * np.abs(interaction_magnitudes))

            # compute new angles by blending the current angles toward the desired angle
            new_angle_i = current_angles_i + alpha * ((((desired_angles - current_angles_i + np.pi) % (2 * np.pi)) - np.pi))
            new_angle_j = current_angles_j + alpha * ((((desired_angles - current_angles_j + np.pi) % (2 * np.pi)) - np.pi))

            speed_i = np.linalg.norm(self._velocity[valid_i], axis=1)
            speed_j = np.linalg.norm(self._velocity[valid_j], axis=1)

            # update velocities with the new directions
            self._velocity[valid_i, 0] = speed_i * np.cos(new_angle_i)
            self._velocity[valid_i, 1] = speed_i * np.sin(new_angle_i)
            self._velocity[valid_j, 0] = speed_j * np.cos(new_angle_j)
            self._velocity[valid_j, 1] = speed_j * np.sin(new_angle_j)
    
    def _wrap_around(self, positions)-> np.ndarray:
        """
        Wraps particle positions around the canvas.
        
        Parameters
        ----------
        positions : np.ndarray
            A 2D array of particle positions.
        
        Returns
        -------
        np.ndarray
            A 2D array of particle positions with wrapping applied.
        """
        wrapped_positions = np.mod(positions, (self.width, self.height))
        return wrapped_positions
    
    
    

if __name__ == "__main__":
    part_sys = ParticleSystem(width=1000, height=1000, color_distribution=[((1, 0, 0, 1), 5, 1, 1)], radius=1, interaction_matrix={(1, 1): 1})
    part_sys.particles = np.array([[999, 999], [1, 1], [2, 2]])
    print(part_sys.check_collisions(part_sys.particles, radius=1))