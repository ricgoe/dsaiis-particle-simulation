import numpy as np
from scipy.spatial import cKDTree
from IntegrityChecks import _validate_particle_entry

class ParticleSystem:
    def __init__(self, width: int, height: int, color_distribution: list[tuple[tuple[int, int, int, int], int, int, int]], interaction_matrix: dict[tuple[int, int], float], radius: int = .5, delta_t: float = 0.3, brownian_std: float = 20, min_vel: float = -10, max_vel: float = 10):
        """
        Initialize a ParticleSystem instance for simulating particle dynamics with collisions and interactions.
        This constructor sets up the simulation area, creates particles with random initial positions,
        colors, restitution coefficients, and masses based on a provided color distribution, and
        initializes particle velocities and interaction parameters.
        
        Parameters
        ----------
        width : int
            The width of the simulation area.
        height : int
            The height of the simulation area.
        color_distribution : list of tuple
            A list where each tuple defines a particle class. Each tuple must contain:
                - A tuple of four integers (r, g, b, a) representing the particle's RGBA color.
                - An integer specifying the number of particles of this class.
                - An integer for the restitution coefficient (how bouncy the particles are).
                - An integer for the mass of the particles.
        interaction_matrix : dict
            A dictionary mapping a pair of particle class indices (tuple of two ints) to their interaction magnitude.
            Positive values indicate attraction, while negative values indicate repulsion.
        radius : float, optional
            The radius of each particle (default is 0.5).
        delta_t : float, optional
            The time step for particle movement updates (default is 0.3).
        brownian_std : float, optional
            The standard deviation for the Brownian (random) motion applied to the particles (default is 20).
        min_vel : float, optional
            The minimum initial velocity magnitude for particles (default is -10).
        max_vel : float, optional
            The maximum initial velocity magnitude for particles (default is 10).
            
        Attributes
        ----------
        _particles : np.ndarray
            A 2D array of shape (N, 2) containing the (x, y) positions of the particles.
        _colors : np.ndarray
            A 2D array of shape (N, 4) containing the RGBA colors of the particles.
        _color_index : np.ndarray
            A 1D array of particle class indices corresponding to each particle.
        _restitution : np.ndarray
            A 1D array of restitution coefficients for the particles.
        _mass : np.ndarray
            A 1D array containing the mass of each particle.
        _velocity : np.ndarray
            A 2D array of shape (N, 2) representing the initial velocities of the particles,
            determined by randomly assigned speeds and directions.
        _interaction_matrix : np.ndarray
            A symmetric matrix (generated from the provided dictionary) containing the scaled interaction
            magnitudes between particle classes.
        _half_life : float
            The half-life constant used in friction calculations (set to 0.04).
        _friction_fact : float
            The friction factor applied to particle velocities, computed based on the half-life and delta_t.
        _interaction_radius : float
            The effective interaction radius for particles, set as 100 times the particle radius.
        _beta : float
            A threshold parameter (set to 0.3) used in force calculations to define regions of interaction.
        """
        self._particles = None
        self._colors = None
        self._color_index = None
        self._width: int = width
        self._height: int = height
        self._radius: int = radius
        self._delta_t: float = delta_t
        self._brownian_std: float = brownian_std
        self._color_distribution = color_distribution
        self._particles, self._colors, self._color_index, self._restitution, self._mass = self.init_particles()
        speeds = np.random.uniform(min_vel, max_vel, self._particles.shape[0])
        angles = np.random.uniform(0, 2 * np.pi, self._particles.shape[0])
        self._velocity = np.column_stack((speeds * np.cos(angles), speeds * np.sin(angles)))
        self._interaction_matrix = interaction_matrix#self.create_interaction_matrix(interaction_matrix) # positive values indicate attraction, negative values indicate repulsion
        # self._interaction_matrix = self.create_interaction_matrix(interaction_matrix) # positive values indicate attraction, negative values indicate repulsion
        print(self._interaction_matrix)
        #self._interaction_matrix = interaction_matrix # needed for other interaction solution
        self._half_life: float = .04
        self._friction_fact = np.pow(0.5, self.delta_t/self._half_life)
        self._interaction_radius = 100*self._radius
        self._beta = 0.3

    
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
        return np.full(self._particles.shape[0], self._radius)
    
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
        self._particles = value
    
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

        for idx, val in enumerate(self._color_distribution.values(), start=1):
            _validate_particle_entry(val["color"], val["n"], val["bounciness"], val["mass"])
            x_coords = np.random.uniform(0, self._width, size=val["n"])
            y_coords = np.random.uniform(0, self._height, size=val["n"])
            positions = np.column_stack((x_coords, y_coords))
            colors = np.tile(np.array(val["color"]), (val["n"], 1))
            color_indices = np.full((val["n"], 1), idx)
            restitutions = np.full((val["n"],), val["bounciness"])
            masses = np.full((val["n"],), val["mass"])
            particles.append((positions, colors, color_indices, restitutions, masses))
            
        positions, colors, color_indices, restitution, mass = map(lambda arrays: np.concatenate(arrays, axis=0), zip(*particles))
    
        return positions, colors, color_indices, restitution, mass


    def move_particles(self):
        """
        Advances the simulation by one time step by updating particle positions and velocities based on 
        Brownian motion, collisions, and interactions.

        The method performs the following steps:
        1. Generates a random Brownian acceleration for each particle using a normal distribution 
            with standard deviation `self._brownian_std`.
        2. Updates the particle velocities by adding the computed acceleration scaled by the time step 
            `self._delta_t`.
        3. Computes tentative new positions using the updated velocities and applies periodic boundary 
            conditions based on the simulation area dimensions (`self._width`, `self._height`).
        4. Detects collisions among particles by calling `check_collisions` with an effective detection 
            radius `self._interaction_radius`.
        5. If no collision data is found, the particle positions are updated to the new positions and 
            the method returns early.
        6. For detected collisions:
            - Identifies colliding pairs where the inter-particle distance is less than or equal to 
            `2 * self._radius` and updates their velocities and positions in "collision" mode via 
            `update_velocities_collisions`.
            - Processes all candidate pairs for interaction effects by invoking `update_velocities_collisions` 
            in "interaction" mode.

        Returns
        -------
        None
            The particle positions and velocities are updated in place.
        """
        
        # set up Brownian acceleration
        acc = np.random.normal(0, self._brownian_std, self._particles.shape)
        self._velocity += self._velocity + acc * self._delta_t # update velocities
        delta_pos = self._velocity*self._delta_t
        new_pos = self._wrap_around(self._particles + delta_pos)
        # detect collisions with tentative new positions
        collision_data: np.ndarray = self.check_collisions(new_pos, radius=self._interaction_radius) # sorted from left to right and bottom to top
        if collision_data.size == 0:
            self._particles = new_pos
            return

        colliding_mask = collision_data[:, 2] <= 2 * self._radius
        if colliding_mask.any():
            self.update_velocities_collisions(new_pos, collision_data[colliding_mask], mode='collision')

        self.update_velocities_collisions(new_pos, collision_data, mode='interaction')


    def create_interaction_matrix(self, matrix: dict):
        int_matrix = np.zeros((len(self._color_distribution), len(self._color_distribution)), dtype=float)
        for (i, j), val in matrix.items():
            i0 = i - 1
            j0 = j - 1
            int_matrix[i0, j0] = val['value']/5
        return int_matrix
    
    
    def check_collisions(self, positions: np.ndarray, radius: float) -> tuple:
        """
        Detects collisions between particles using a spatial tree.
        
        Parameters
        ----------
        positions : np.ndarray
            A 2D array of particle positions.
        radius : float
            The radius used for collision detection.
        
        Returns
        -------
        np.ndarray
            A 2D array of shape (N, 5) containing the following columns:
            - i_idx : indices for the first particle in each colliding pair.
            - j_idx : indices for the second particle.
            - distances : distances between colliding particles.
            - normals : unit vectors pointing from the second particle to the first
        """
        # boxsize=[self._width, self._height] is necessary for periodic boundaries
        tree = cKDTree(positions, boxsize=[self._width, self._height])
        pairs = tree.query_pairs(r=radius)
        if not pairs:
            return np.empty(0)
        
        pairs_arr = np.fromiter((i for pair in pairs for i in pair), dtype=int).reshape(-1, 2)
        coll_arr = np.zeros((pairs_arr.shape[0], 5))
        i_idx = pairs_arr[:, 0]
        j_idx = pairs_arr[:, 1]
        
        
        # compute differences in x and y, wrap around boundaries
        dx = (positions[i_idx, 0] - positions[j_idx, 0] + self._width/2) % self._width - self._width/2
        dy = (positions[i_idx, 1] - positions[j_idx, 1] + self._height/2) % self._height - self._height/2
        distances = np.sqrt(dx**2 + dy**2)
        
        coll_arr[:,:2] = pairs_arr
        coll_arr[:,2] = distances
        coll_arr[:,3] = dx
        coll_arr[:,4] = dy

        distances_safe = np.where(distances == 0, 1, distances)
        coll_arr[:,3:] /= distances_safe[:, None]
        
        return coll_arr
    
     
    def update_velocities_collisions(self, positions: np.ndarray, colliding_data: np.ndarray, mode: str = "collision") -> None:
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
            - "interaction": Update velocities and positions based on interactions between particles.
            (default is "collision").
        
        Returns
        -------
        None
        """
        i_idx, j_idx = colliding_data[:,0].astype(int), colliding_data[:,1].astype(int)
        normals = colliding_data[:,3:]
        distances = colliding_data[:,2]
        if mode == "collision":
            # calculate overlap (depth) for each collision
            depth = 2 * self._radius - distances
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
            self.calculate_interaction_accelerations(i_idx, j_idx, distances, normals)

            # # compute vector from particle j to particle i
            # direction = self._particles[i_idx] - self._particles[j_idx]  # shape (n, 2)
            # norms = np.linalg.norm(direction, axis=1)  # shape (n,)

            # valid = norms > 0
            # if not np.any(valid):
            #     return 

            # valid_i = i_idx[valid]
            # valid_j = j_idx[valid]
            # direction_valid = direction[valid]
            # norms_valid = norms[valid]
            # normals = direction_valid / norms_valid[:, None]

            # # compute desired angles from the normals
            # desired_angles = np.arctan2(normals[:, 1], normals[:, 0])

            # colors_i = self._color_index[valid_i, 0]
            # colors_j = self._color_index[valid_j, 0]
            # min_colors = np.minimum(colors_i, colors_j)
            # max_colors = np.maximum(colors_i, colors_j)
            # lookup = np.vectorize(lambda a, b: self._interaction_matrix[(a, b)]["value"])
            # interaction_magnitudes = lookup(min_colors, max_colors)

            # # repulsive interactions, adjust desired angle by π
            # repulsive = interaction_magnitudes < 0
            # desired_angles[repulsive] = (desired_angles[repulsive] + np.pi) % (2 * np.pi)

            # # get current angles of velocities for particles i and j
            # current_angles_i = np.arctan2(self._velocity[valid_i, 1], self._velocity[valid_i, 0])
            # current_angles_j = np.arctan2(self._velocity[valid_j, 1], self._velocity[valid_j, 0])

            # alpha = np.where(interaction_magnitudes > 0,
            #                 0.05 * np.abs(interaction_magnitudes),
            #                 0.1 * np.abs(interaction_magnitudes))

            # # compute new angles by blending the current angles toward the desired angle
            # new_angle_i = current_angles_i + alpha * ((((desired_angles - current_angles_i + np.pi) % (2 * np.pi)) - np.pi))
            # new_angle_j = current_angles_j + alpha * ((((desired_angles - current_angles_j + np.pi) % (2 * np.pi)) - np.pi))

            # speed_i = np.linalg.norm(self._velocity[valid_i], axis=1)
            # speed_j = np.linalg.norm(self._velocity[valid_j], axis=1)

            # # update velocities with the new directions
            # self._velocity[valid_i, 0] = speed_i * np.cos(new_angle_i)
            # self._velocity[valid_i, 1] = speed_i * np.sin(new_angle_i)
            # self._velocity[valid_j, 0] = speed_j * np.cos(new_angle_j)
            # self._velocity[valid_j, 1] = speed_j * np.sin(new_angle_j)
    
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
        wrapped_positions = np.mod(positions, (self._width, self._height))
        return wrapped_positions


    def force(self, dist: np.ndarray, int_coef: np.ndarray) -> np.ndarray:
        """
        Compute the interaction force magnitude based on particle distance and interaction coefficient.

        The force is calculated by first scaling the distances `dist` by  `self._interaction_radius`. A piecewise
        function is then applied based on the scaled distance relative to a threshold value `self._beta`:
        
        - Region 1: For scaled distances less than `self._beta`, the force increases linearly from -1 to 0.
        - Region 2: For scaled distances between `self._beta` and 1, the force is modulated by the interaction
          coefficient `int_coef` and decreases linearly.

        Parameters
        ----------
        dist : np.ndarray
            The distances between interacting particles.
        int_coef : np.ndarray
            The interaction coefficient(s) corresponding to the particles. Positive values indicate attraction,
            whereas negative values indicate repulsion.

        Returns
        -------
        np.ndarray
            An array of force magnitudes computed for each distance in `dist`.
        """
        dist = np.asarray(dist/self._interaction_radius)
        int_coef = np.asarray(int_coef).reshape(-1)
    
        forces = np.zeros_like(dist, dtype=float)

        # region 1: r < beta
        mask1 = (dist < self._beta)
        forces[mask1] = (dist[mask1] / self._beta) - 1

        # region 2: beta < r < 1
        mask2 = (dist > self._beta) & (dist < 1)
        forces[mask2] = int_coef[mask2] * (
            1 - (np.abs(2*dist[mask2] - 1 - self._beta) / (1 - self._beta))
        )
        return forces
        
        
    def calculate_interaction_accelerations(self, i_idx: np.ndarray, j_idx: np.ndarray, distances: np.ndarray, normals: np.ndarray) -> np.ndarray:
        """
        Compute and apply accelerations resulting from particle interactions.

        For each interacting particle pair defined by the indices in `i_idx` and `j_idx`, this method:
          1. Retrieves the corresponding interaction coefficient from the interaction matrix using each particle's color index.
          2. Computes the interaction force magnitude via the `force` method based on the distance between particles.
          3. Applies the force along the negative of the provided normal direction to obtain a force vector.
          4. Accumulates these force vectors into an acceleration array.
          5. Scales the accumulated acceleration by the interaction radius and a constant factor (40),
             then normalizes it by the particle masses.
          6. Applies a friction factor to the current velocities.
          7. Updates the velocities using the computed acceleration and time step.
          8. Updates the particle positions with periodic boundary conditions.

        Parameters
        ----------
        i_idx : np.ndarray
            Array of indices for the first particle in each interacting pair.
        j_idx : np.ndarray
            Array of indices for the second particle in each interacting pair.
        distances : np.ndarray
            Array of distances between each interacting particle pair.
        normals : np.ndarray
            Array of normalized direction vectors for each pair.

        Returns
        -------
        None
        """
        interaction_matrix = self.create_interaction_matrix(self._interaction_matrix)
        int_coef = interaction_matrix[self._color_index[i_idx]-1, self._color_index[j_idx]-1]
        forces = self.force(distances, int_coef)
        forces_norm = -normals*forces[:, None]
        acc = np.zeros(self._particles.shape)
        np.add.at(acc, i_idx, forces_norm)
        acc*=self._interaction_radius*40
        acc /= self._mass[:, np.newaxis]
        self._velocity *= self._friction_fact
        self._velocity = acc*self.delta_t
        self._particles = np.mod(self._particles + self._velocity*self.delta_t, (self._width, self._height))


    @DeprecationWarning
    def dep_update_velocities_collisions(self, positions: np.ndarray, colliding_data: np.ndarray, mode: str = "collision") -> None:
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
            - "interaction": Update velocities and positions based on interactions between particles.
            (default is "collision").
        
        Returns
        -------
        None
        """
        i_idx, j_idx = colliding_data[:,0].astype(int), colliding_data[:,1].astype(int)
        normals = colliding_data[:,3:]
        distances = colliding_data[:,2]
        if mode == "collision":
            # calculate overlap (depth) for each collision
            depth = 2 * self._radius - distances
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
            lookup = np.vectorize(lambda a, b: self._interaction_matrix[(a, b)]["value"])
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
        

if __name__ == "__main__":
    import threading
    color_distribution = {
        "key1": { "color": (1.0, 0.0, 0.0, 1.0), "n": 375, "mass": 1, "bounciness": 1.0,},
        "key2": { "color": (0.0, 0.0, 1.0, 1.0),"n": 375,"mass": 1,"bounciness": 1.0,}
    }
    
    relationships = {
        (1, 1): {"value": 0},
        (1, 2): {"value": 0},
        (2, 1): {"value": 0},
        (2, 2): {"value": 0},
    }
    part_sys = ParticleSystem(1000, 800, color_distribution, relationships, radius=1, delta_t = 0.0166)
    def rapat(n_times_left):
        if n_times_left > 0:
            threading.Timer(0.0166, rapat, (n_times_left - 1)).start()
        part_sys.move_particles()
    rapat(1000)