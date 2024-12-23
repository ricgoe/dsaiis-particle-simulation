import numpy as np
import matplotlib.pyplot as plt

class ParticleSystem:
    def __init__(self, width: int, height: int, color_distribution: list[tuple[tuple[int, int, int], int]], step_size: float = 2, radius: int = 10, mass: int = 1, delta_t: float = 0.05, **kwargs):
        self.color_distribution = color_distribution
        self.width: int = width
        self.height: int = height
        self.radius: int = radius
        self.mass: int = mass
        self.velocity: float = 0
        self.collsion_movement: float = 0
        self.delta_t: float = delta_t
        self.override = kwargs.get('override', False)
        self._particles = self.init_particles() if not self.override else self.hardcoded_particles_pos()
        print(self._particles)
        self.step_size: float = step_size
        self.move_arr = np.array([[.5, .5], [-.5, .5]])
        
    
    @property
    def particles(self):
        return self._particles
    
    def init_particles(self):
        part_arrays = []
        for rgba, num_part in self.color_distribution:
            tmp_arr = np.random.uniform(0, self.width, size=(num_part, 2))
            rgba_repeated = np.repeat(np.array(rgba)[None, :], repeats=num_part, axis=0)
            combined_arr = np.concatenate([tmp_arr, rgba_repeated], axis=1)
            part_arrays.append(combined_arr)
        
        full_array = np.concatenate(part_arrays, axis=0)
        l_r_array = self.calc_l_r(full_array, action_radius=5)
        return l_r_array
    
    def hardcoded_particles_pos(self):
        arr = np.array([[5, 5, 255, 0, 0, 255], [15, 5, 0, 255, 0, 255]])
        arr = self.calc_l_r(arr, action_radius=2) # add left and right coordinates
        return arr
        
    def move_particles(self):
        move_arr = np.random.normal(0, self.step_size, size=(self.particles.shape[0], 2))
        self.velocity = move_arr / self.delta_t
        self.calc_collsion_movement(k=1)
        self._particles = np.mod(self._particles[:,:2] + move_arr + self.collsion_movement, (self.width, self.height))
        
    def move_controlled(self):
        new_arr = np.array((self.move_arr[:,0], self.move_arr[:,0])).T
        expanded_l_r_array = np.hstack([new_arr, self.move_arr])
        self.velocity = self.move_arr / self.delta_t
        #self.calc_collsion_movement(k=.001)
        self._particles = np.mod(self._particles[:,:4] + expanded_l_r_array + self.collsion_movement, (self.width, self.width, self.width, self.height))
        self._particles = self.sort_by_left(self._particles)
        

    def calc_l_r(self, array, action_radius = None):
        # calculate left and right coordinates of each particle
        action_radius = action_radius if action_radius else self.radius
        l_r = np.mod([array[:,0]-action_radius, array[:,0]+action_radius], self.width).T
        new_array = np.concatenate([l_r, array], axis=1)
        return new_array
    

    def sort_by_left(self, array): #  sorts the array by the first column
        indices = np.argsort(array[:,0], kind = 'quicksort')
        sorted_arr = array[indices]
        self.move_arr = self.move_arr[indices]
        return sorted_arr
        
    def check_collision(self):
        coll_arr = np.full((self._particles.shape[0], 4), min(self.width, self.height)*10, dtype=np.float32) # particle 1, particle 2, distance
        # TODO: find a value that is small but delivers a negative result in force_arr
        for i in range(self._particles.shape[0]):
            for j in range(i+1, self._particles.shape[0]):
                if self._particles[j, 0] > self._particles[i, 1]:
                    print('particles not colliding')
                    break
                intersection, dist, angle = self.check_intersection(self._particles[i], self._particles[j])
                if intersection:
                    print(f'particles {i} and {j} colliding with distance {dist}')
                    coll_arr[i] = [i , j, dist, angle]
                    coll_arr[j] = [j , i, dist, angle]
        
        return coll_arr
    
    def calc_col_force_arr(self, k: float, collision_arr: np.ndarray):
        # k = stiffness
        # TODO: add different radii for each color
        force_arr = ((np.maximum(0, 2 * self.radius - collision_arr[:, 2]) * k * np.array([np.cos(collision_arr[:, 3] * np.pi/180), np.sin(collision_arr[:, 3] * np.pi/180)]))/self.mass)*self.delta_t
        print(force_arr)
        self.velocity += force_arr
        
        return force_arr * self.delta_t
    
    def check_intersection(self, particle1, particle2): # in case the particles overlap in the x-direction check if they overlap in the y-direction --> they are colliding
        dist = np.sqrt(np.sum((particle1[2:4] - particle2[2:4])**2))
        angle = np.degrees(np.arctan((particle2[3] - particle1[3])/ (particle2[2] - particle1[2])))
        print(f'angle: {angle}')
        if dist < 2 * self.radius:
            return (True, dist, angle)
        else:   
            return (False, -1, -1)
        
    def calc_collsion_movement(self, k: float):
        col_arr = self.check_collision()
        print(col_arr)
        movement = self.calc_col_force_arr(k=k, collision_arr=col_arr)
        new_arr = np.array((movement[:,0], movement[:,0])).T
        expanded_l_r_array = np.hstack([new_arr, movement])
        
        self.collsion_movement = expanded_l_r_array
        

    def plot_particles(self):
        plt.ion()
        fig, ax = plt.subplots()
        ax.set_xlim(0, self.width)
        ax.set_ylim(0, self.height)

        while True:
            ax.clear()
            ax.set_xlim(0, self.width)
            ax.set_ylim(0, self.height)
            ax.scatter(self._particles[:,2], self._particles[:,3], color='r', s=10)
            print(self._particles)
                
            plt.pause(0.05) 
            self.move_controlled()
            self.check_collision()

            
        

if __name__ == "__main__":
    part_sys = ParticleSystem(width=20, height=20, color_distribution=[((255, 0, 0, 255), 1), ((0, 255, 0, 255), 1)], step_size=.5, radius=1, override = True)
    part_sys.plot_particles()