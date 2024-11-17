import numpy as np
from particle import Particle
from matplotlib import pyplot as plt

class ParticleSystem:
    def __init__(self, width: int, height: int, color_distribution: list[tuple[tuple[int, int, int], int]], step_size: float = 5, radius: int = 10, min_distance: float = 500):
        self.color_distribution = color_distribution
        self.width: int = width
        self.height: int = height
        self._particles: list[Particle] = self.init_particles()
        self.step_size: float = step_size
        self.min_distance: float = min_distance
    
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
            
            # normaler step wie vorher, *0.2 , weil sonst zu viel anteil an randomness. 0.2 erstaml zufällig gewählt
            step = np.random.normal(0, self.step_size, 2)
            new_x = (particle.x_pos + 0.2 * step[0])
            new_y = (particle.y_pos + 0.2 * step[1])

            # anziehung und abstoßung
            repulsion_x, repulsion_y = 0, 0
            attraction_x, attraction_y = 0, 0
            for other in self.particles:

                # distanz zu jedem anderen particle
                x_distance = particle.x_pos - other.x_pos
                y_distance = particle.y_pos - other.y_pos
                distance = np.sqrt(x_distance**2 + y_distance**2)


                if distance > 0:
                    
                    # bei unterschiedlicher farbe: abstoßung und wenn in der distanz liegt, die beeinflusst werden soll
                    if particle.color != other.color and distance < self.min_distance:

                    
                        # force ist min.distance - distance, damit größer, wenn abstand kleiner
                        force = (self.min_distance - distance) 
                        # columbsche abstand mal die berechnete force geteilte durch erstmal random parameter, der gut gepasst hat
                        repulsion_x += (x_distance/distance) * force / (self.min_distance / 2)
                        repulsion_y += (y_distance/distance) * force / (self.min_distance / 2)

                        
                    # bei gleicher farbe: anziehung
                    elif particle.color == other.color and distance < self.min_distance:

                        
                        force = (self.min_distance - distance) 
                        attraction_x += (x_distance/distance) * force / (self.min_distance / 2)
                        attraction_y += (y_distance/distance) * force / (self.min_distance / 2)

                        
            # anziehung das gegenteil von abstoßung, deswegen anziehung abgezogen und abstoßung addiert zu neuen koordinaten
            new_x = np.mod(new_x + repulsion_x - attraction_x, self.width)
            new_y = np.mod(new_y + repulsion_y - attraction_y, self.height)

            particle.move(new_x, new_y)
            
    def check_collision(self):
        pass

    

    def plot_particles(self):
        self.init_particles()
        plt.ion()
        fig, ax = plt.subplots()
        ax.set_xlim(0, self.width)
        ax.set_ylim(0, self.height)

        while True:
            ax.clear()
            ax.set_xlim(0, self.width)
            ax.set_ylim(0, self.height)
            for particle in self.particles:
                col = (particle.color[0]/255, particle.color[1]/255, particle.color[2]/255)
                ax.scatter(particle.x_pos, particle.y_pos, color=col)
                
            plt.pause(0.01) 
            self.move_particles()

            
if __name__ == "__main__":
    particle_system = ParticleSystem(width=1000, height=1000, color_distribution=[((255, 0, 0), 20), ((0, 255, 0), 20), ((0, 0, 255), 20)], step_size= 10)
    particle_system.plot_particles()
    