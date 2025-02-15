import numpy as np
from scipy.spatial import cKDTree

class ParticleSystem:
    def __init__(self, width: int, height: int, color_distribution: list[tuple[tuple[int, int, int, int], int, int, int]], interaction_matrix: dict[tuple[int, int], float], radius: int = .5, delta_t: float = 0.3, brownian_std: float = .01, drag: float = 0.5, min_vel: float = -1, max_vel: float = 1):
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
                np.full((num, 1), idx),
                np.full((num,), restitution),
                np.full((num,), mass)
            ) 
            for idx, (rgba, num, restitution, mass) in enumerate(self._color_distribution, start=1)
        ]
        positions, colors, color_indices, restitution, mass = map(lambda arrays: np.concatenate(arrays, axis=0), zip(*particles))
    
        return positions, colors, color_indices, restitution, mass
    
    
    def angle_between(self, x, y):
        # compute the angle between the positive x-axis and [x, y]
        angle_rad = np.arctan2(y, x)
        angle_deg = np.degrees(angle_rad) % 360
        return angle_deg
    

    def move_particles(self, skip_interaction: bool = False):
        """
        Moves particles for one timestep and updates their velocities based on collision responses.
        The velocity is set in the constructor. The energy stored in the system stays the same, because only the angles change.
        
        The method uses the current velocity to update particle positions, detects collisions, and then
        updates the velocity for each colliding pair by calling update_velocities_collisions.
        The particles’ positions are then updated with the velocities changed in their angles.
        
        Returns:
            Nones
        """
  
        interaction_radius = 20
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
        new_pos = np.mod(self._particles + delta_pos, (self.width, self.height))
        ghosts, ghost_indices = self.get_ghosts(new_pos, interaction_radius=interaction_radius)
        
        extended_positions = np.vstack((new_pos, ghosts))
        # detect collisions with tentative new positions
        collision_data = self.check_collisions(extended_positions, radius=self.radius, ghost_indices = ghost_indices) # sorted from left to right and bottom to top
        if collision_data[0].size == 0:
            self._particles = new_pos
            return

        # TODO: not relevant for now, maye later
        # increments = self.get_brwn_increment_from_involved_particles(collision_data) # get the delta v's from the particles that are involved in the collision
        # resulting_vector = np.sum(delta_pos[increments], axis=0) # calculate the resulting vector from the brwn increments
        # if np.sum(resulting_vector) == 0: # if the resulting vector is zero, there is no movement
        #     return
        # angle = int(self.angle_between(resulting_vector[0], resulting_vector[1])) # calculate the angle between the resulting vector and the positive x-axis
        # if angle <= 90 or angle > 270:
        #     colliding_pairs.flip() # if the angle is less than 90 or greater than 270, reverse the order of the colliding pairs
        
        self.update_velocities_collisions(new_pos, collision_data, mode='collision')
        # For interaction mode, assuming check_collisions returns candidate pairs when mode != 'collision'
        if interaction_radius and not skip_interaction:
            interaction_candidates = self.check_collisions(extended_positions, radius=interaction_radius, ghost_indices=ghost_indices)
            self.update_velocities_collisions(new_pos, interaction_candidates, mode='interaction')

    def get_ghosts(self, new_pos, interaction_radius):
        
        near_left = new_pos[:, 0] < interaction_radius
        near_right = new_pos[:, 0] > self.width - interaction_radius
        near_top = new_pos[:, 1] > self.height - interaction_radius
        near_bottom = new_pos[:, 1] < interaction_radius

        left_ghost = new_pos[near_left].copy()
        left_ghost[:, 0] = (left_ghost[:, 0] - interaction_radius)%self.width
        left_ghost_indices = np.where(near_left)[0]
        right_ghost = new_pos[near_right].copy()
        right_ghost[:, 0] = (right_ghost[:, 0] + interaction_radius)%self.width
        right_ghost_indices = np.where(near_right)[0]
        top_ghost = new_pos[near_top].copy()
        top_ghost[:, 1] = (top_ghost[:, 1] + interaction_radius)%self.height
        top_ghost_indices = np.where(near_top)[0]
        bottom_ghost = new_pos[near_bottom].copy()
        bottom_ghost[:, 1] = (bottom_ghost[:, 1] - interaction_radius)%self.height
        bottom_ghost_indices = np.where(near_bottom)[0]

        ghosts= np.vstack((left_ghost, right_ghost, top_ghost, bottom_ghost))
        ghost_indices = np.hstack((left_ghost_indices, right_ghost_indices, top_ghost_indices, bottom_ghost_indices))
        return ghosts, ghost_indices

    def calculate_drag(self):
        drag = 0.5*self._velocity**2
        self._velocity *= (1-(0.5*drag)**2)
        

    def get_brwn_increment_from_involved_particles(self, collision_data: tuple) -> np.ndarray:
        # Unpack the tuple: i_idx and j_idx are arrays of indices for collision data
        i_idx, j_idx, _, _ = collision_data
        return np.unique(np.concatenate((i_idx, j_idx)))
    
    
    def check_collisions(self, positions: np.ndarray, radius: float, ghost_indices) -> tuple:
        """
        Uses cKDTree to find colliding pairs of particles.
        
        Parameters:
            positions (np.ndarray): Array of shape (N, 2) with particle positions.
            radius (float): The search radius for each particle.
            
        Returns:
            i_idx (np.ndarray): Indices of the first particle in each colliding pair.
            j_idx (np.ndarray): Indices of the second particle.
            distances (np.ndarray): Distances between the colliding particles.
            normals (np.ndarray): Unit normal vectors from particle i to j.
        """
        tree = cKDTree(positions)
        pairs = tree.query_pairs(r=2*radius)
        
        if not pairs: # no collisions found
            return (np.empty(0, dtype=int),
                    np.empty(0, dtype=int),
                    np.empty(0),
                    np.empty((0, 2)))
        
        pairs_arr = np.array(list(pairs), dtype=int)  # shape (M, 2)
        i_idx = pairs_arr[:, 0]
        j_idx = pairs_arr[:, 1]

        max_real_index = self._particles.shape[0]
        mask = i_idx >= max_real_index
        i_idx_new = i_idx.copy()
        i_idx_new[mask] = ghost_indices[i_idx[mask] - max_real_index]
        i_idx = i_idx_new

        mask = j_idx >= max_real_index
        j_idx_new = j_idx.copy()
        j_idx_new[mask] = ghost_indices[j_idx[mask] - max_real_index]
        j_idx = j_idx_new

        unique_mask = i_idx < j_idx
        i_idx, j_idx = i_idx[unique_mask], j_idx[unique_mask]
        pairs = np.column_stack((i_idx, j_idx))
        unique_pairs = np.unique(pairs, axis=0)
        i_idx, j_idx = unique_pairs[:, 0], unique_pairs[:, 1]
        
        dx = positions[i_idx, 0] - positions[j_idx, 0]
        dy = positions[i_idx, 1] - positions[j_idx, 1]
        dx = (dx + self.width/2) % self.width - self.width/2
        dy = (dy + self.height/2) % self.height - self.height/2

        distances = np.sqrt(dx**2 + dy**2)
        
        # compute normals (handling the zero distance case).
        normals = np.column_stack((dx, dy))#[valid]
        distances_safe = np.where(distances == 0, 1, distances)
        normals = normals / distances_safe[:, None]
        
        
        return i_idx, j_idx, distances, normals
      
      
    def update_velocities_collisions(self, positions: np.ndarray, colliding_data, mode: str = "collision") -> None:
        """
        Updates velocities (and positions) based on collisions
        
        Parameters:
            positions (np.ndarray): Current particle positions.
            colliding_data (tuple): (i_idx, j_idx, distances, normals)
            mode (str): Either "collision" or "interaction".
        
        Returns:
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

if __name__ == "__main__":
    part_sys = ParticleSystem(width=1000, height=1000, color_distribution=[((1, 0, 0, 1), 2, 1, 1)], radius=1, interaction_matrix={(1, 1): 1})
    # part_sys.particles = np.array([[1, 500], [999, 500], [2, 500]])
    part_sys.particles = np.array([[999, 999], [1, 1]])
    gh, gi = part_sys.get_ghosts(part_sys.particles, interaction_radius= 10)
    extended_positions = np.vstack((part_sys.particles, gh))
    print(extended_positions)
    print(part_sys.check_collisions(extended_positions, radius=10, ghost_indices = gi))