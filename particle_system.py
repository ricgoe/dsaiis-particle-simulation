import numpy as np

class ParticleSystem:
    def __init__(self, width: int, height: int, color_distribution: list[tuple[tuple[int, int, int], int]], step_size: float = 2, radius: int = 10):
        self.color_distribution = color_distribution
        self.width: int = width
        self.height: int = height
        self.radius: int = radius
        self._particles = self.init_particles()
        self.step_size: float = step_size

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
        
        return np.concatenate(part_arrays, axis=0)


    
    def move_particles(self):
        move_arr = np.random.normal(0, self.step_size, size=(self.particles.shape[0], 2))
        self._particles[:,:2] = np.mod(self._particles[:,:2] + move_arr, (self.width, self.height)) 

    def collsion_check(self):
        pass
    
    def create_bounding_boxes(self):
        # create bounding boxes for each particle only on x axis
        lower_x, upper_x = np.mod(self._particles[:,0] - self.radius, self.width), np.mod(self._particles[:,0] + self.radius, self.width)
        #lower_y, upper_y = self._particles[:,1] - self.radius, self._particles[:,1] + self.radius
        
        #bounding_boxes = da.stack([lower_x, upper_x, lower_y, upper_y], axis=1)
        bounding_boxes = np.stack([lower_x, upper_x], axis=1)
        
        return bounding_boxes
    
    def create_collsion_array(self):
        bounding_boxes = self.create_bounding_boxes()
        
    def naive_collsion_check(self):
        for part in self._particles[:,:2]:
            for other_part in self._particles[:,:2]:
                if 0 < np.sqrt(np.sum((part - other_part)**2)) < self.radius:
                    print('collsion')
            
        

if __name__ == "__main__":
    part_sys = ParticleSystem(width=100, height=100, color_distribution=[((1, 0, 0, 1), 1), ((0, 1, 0, 1), 1)], step_size=.5, radius=.5)
    #print(part_sys.particles.compute())
    #part_sys.create_collsion_array()
    print(part_sys.particles[:, 2:])
   
    # while True:
    #     part_sys.move_particles()
    #     part_sys.naive_collsion_check()
    