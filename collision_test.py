import numpy as np

class test_ParticleSystem:
    def __init__(self, width = 100, height = 100, radius: int = 10):
        
        self.width: int = width
        self.height: int = height
        self.radius: int = radius
        self._particles = self.init_particles()


    @property
    def particles(self):
        return self._particles
    
    def init_particles(self):
        part_arrays = []
        
        tmp_arr = np.array([[100, 100], [0, 100]])
        rgba_repeated = np.array([[1, 0, 0, 1], [0, 1, 0, 1]])
        combined_arr = np.concatenate([tmp_arr, rgba_repeated], axis=1)
        part_arrays.append(combined_arr)
        
        return np.concatenate(part_arrays, axis=0)


    
    def move_particles(self):
        move_arr = np.array([[-1, -1], [1, -1]])
        self._particles[:,:2] = np.mod(self._particles[:,:2] + move_arr, (self.width, self.height)) 


if __name__ == "__main__":
    part_sys = test_ParticleSystem(width=100, height=100, color_distribution=[((1, 0, 0, 1), 1), ((0, 1, 0, 1), 1)], step_size=.5, radius=.5)
