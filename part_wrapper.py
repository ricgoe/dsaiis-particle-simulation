import numpy as np
from particle import Particle

class ParticleSystem:
    def __init__(self, width: int, height: int, color_distribution: list[tuple[tuple[int, int, int], int]], step_size: float = 5, radius: int = 10):
        self.color_distribution = color_distribution
        self.width: int = width
        self.height: int = height
        self._particles: list[Particle] = self.init_particles()
        self.step_size: float = step_size
    
    @property
    def particles(self):
        return self._particles
    
    def init_particles(self):
        tmp = []
        for rgb, num in self.color_distribution:
            __x = np.random.uniform(0, self.width, num)
            __y = np.random.uniform(0, self.height, num)
            for x, y in zip(__x, __y):
                tmp.append(Particle(color=rgb, x_pos=x, y_pos=y))
        return tmp
                
    def move_particles(self):
        for particle in self.particles:
            # step = np.random.normal(0, self.step_size, 2)
            x_step = np.random.normal(0, self.step_size)
            y_step = np.random.normal(0, self.step_size)
            new_x = np.mod(particle.x_pos + x_step, self.width)
            new_y = np.mod(particle.y_pos + y_step, self.height)
            particle.move(new_x, new_y)
            
    def check_collision(self):
        pass


            
if __name__ == "__main__":
    particle_system = ParticleSystem(width=1000, height=1000, color_distribution=[((255, 0, 0), 100)], step_size= 10)
    