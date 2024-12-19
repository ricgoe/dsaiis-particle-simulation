import numpy as np
from dask import array as da

class ParticleSystem:
    def __init__(self, width: int, height: int, color_distribution: list[tuple[tuple[int, int, int], int]], step_size: float = 5, radius: int = 10, chunk_size: int = 1000):
        self.color_distribution = color_distribution
        self.width: int = width
        self.height: int = height
        self.chunk_size: int = chunk_size
        self._particles = self.init_particles()
        self.step_size: float = step_size
    
    @property
    def particles(self):
        return self._particles
    
    def init_particles(self):
        part_arrays = []
        for rgba, num_part in self.color_distribution:
            tmp_arr = da.random.uniform(0, self.width, size=(num_part, 2), chunks=(self.chunk_size, self.chunk_size))
            rgba_dask = da.from_array(rgba, chunks=(4,))
            rgba_repeated = da.repeat(rgba_dask[None, :], repeats=num_part, axis=0)
            combined_arr = da.concatenate([tmp_arr, rgba_repeated], axis=1)
            part_arrays.append(combined_arr)
        
        part_array = da.concatenate(part_arrays, axis=0)
        return part_array


    
    def move_particles(self):
        move_arr = da.random.normal(0, self.step_size, size=(self.particles.shape[0], 2), chunks=(self.chunk_size, self.chunk_size))
        new_positions = da.mod(self._particles[:,:2] + move_arr, self.width)
        self._particles = new_positions.persist()
        self._particles.compute()


        

if __name__ == "__main__":
    import time
    part_sys = ParticleSystem(width=1000, height=1000, color_distribution=[((255, 0, 0, 255), 5000), ((0, 255, 0, 255), 5000)])
    
    start = time.time()
    for i in range(1000):
        start = time.time()
        part_sys.move_particles()
        end = time.time()
        print(end - start)

    