import numpy as np
from particle import Particle
from scipy.spatial import KDTree
import numba
from numba.typed import List

class ParticleSystem:

    def __init__(self, width: int, height: int, color_distribution: list[tuple[tuple[int, int, int], int]], step_size: float = 2, radius: int = 10, min_distance: float = 300):


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
        for rgba, num in self.color_distribution:
            __x = np.random.uniform(0, self.width, num)
            __y = np.random.uniform(0, self.height, num)
            for x, y in zip(__x, __y):
                tmp.append(Particle(color=rgba, x_pos=x, y_pos=y))
        return tmp
                
    def move_particles(self):
        positions = np.array([(p.x_pos, p.y_pos) for p in self.particles])
        colors = np.array([p.color for p in self.particles])

        neighbors = self.check_neighbors(positions = positions) 
        # neighbors = np.array(neighbors)

        new_positions = move_particles_numba(positions, colors,self.step_size, self.min_distance, self.width, self.height, neighbors)

        for idx, particle in enumerate(self.particles):
            particle.move(new_positions[idx, 0], new_positions[idx, 1])
            
    def check_edge_neighbors(self, particle, tree):
        edge_particles = []

        if particle[0] < self.width + self.min_distance:
            mirrored_particles = tree.query_ball_point((particle[0] + self.width, particle[1]), r=self.min_distance)
            edge_particles.extend(mirrored_particles)

        elif particle[0] > self.width - self.min_distance:
            mirrored_particles = tree.query_ball_point((particle[0] - self.width, particle[1]), r=self.min_distance)
            edge_particles.extend(mirrored_particles)

        if particle[1] < self.height + self.min_distance:
            mirrored_particles = tree.query_ball_point((particle[0], particle[1] + self.height), r=self.min_distance)
            edge_particles.extend(mirrored_particles)

        elif particle[1] > self.height - self.min_distance:
            mirrored_particles = tree.query_ball_point((particle[0], particle[1] - self.height), r=self.min_distance)
            edge_particles.extend(mirrored_particles)

        return edge_particles
        
    def check_neighbors(self, positions):
        
        tree = KDTree(positions)

        neighbors = List()

        for particle in positions:

            particle_neighbors = tree.query_ball_point((particle[0], particle[1]), r=self.min_distance)
            particle_neighbors.extend(self.check_edge_neighbors(particle, tree))

            neighbors.append(List(particle_neighbors))
                
        return neighbors
        
@numba.njit #tenk
def move_particles_numba(positions, colors, step_size, min_distance, width, height, neighbors):	
        new_positions = np.copy(positions)
        num_particles = len(positions)

        for particle in range(num_particles):

            step = np.random.normal(0, step_size, 2)
            new_x = (positions[particle, 0] + 0.2 * step[0])
            new_y = (positions[particle, 1] + 0.2 * step[1])

            repulsion_x, repulsion_y = 0, 0
            attraction_x, attraction_y = 0, 0

            

            for j in neighbors[particle]:

                # if positions[particle, 0] == positions[j, 0] and positions[particle, 1] == positions[j, 1]:
                #     continue

                # distanz zu jedem anderen particle
                x_distance = positions[particle, 0] - positions[j,0]
                y_distance = positions[particle, 1] - positions[j, 1]

            
                if x_distance > min_distance:
                    x_distance = 0 - (width - x_distance)
                    
                if y_distance > min_distance:
                    y_distance = 0 - (height - y_distance)
                    

                if x_distance < -min_distance:
                    x_distance = width - abs(x_distance)

                if y_distance < -min_distance:
                    y_distance = height - abs(y_distance)


                    

                distance = np.sqrt(x_distance**2 + y_distance**2)


                if distance < min_distance and distance > 0: #???
                    
                    # bei unterschiedlicher farbe: abstoßung und wenn in der distanz liegt, die beeinflusst werden soll
                    if colors[particle][0] != colors[j][0] or colors[particle][1] != colors[j][1] or colors[particle][2] != colors[j][2]:

                    
                        # force ist min.distance - distance, damit größer, wenn abstand kleiner
                        # force = (self.min_distance - distance) 
                        # columbsche abstand mal die berechnete force geteilte durch erstmal random parameter, der gut gepasst hat
                        repulsion_x += (x_distance/distance) #* force / (self.min_distance / 2)
                        repulsion_y += (y_distance/distance) #* force / (self.min_distance / 2)

                        
                    # bei gleicher farbe: anziehung
                    elif colors[particle][0] == colors[j][0] and colors[particle][1] == colors[j][1] and colors[particle][2] == colors[j][2]:

                        
                        'force = (self.min_distance - distance)' 
                        attraction_x += (x_distance/distance)  #* force / (self.min_distance / 2)
                        attraction_y += (y_distance/distance) #* force / (self.min_distance / 2)
            
            force_x = (repulsion_x - attraction_x)
            force_y = (repulsion_y - attraction_y)
            new_x = np.mod(new_x + force_x, width)
            new_y = np.mod(new_y + force_y, height)

            new_positions[particle][0] = new_x
            new_positions[particle][1] = new_y
            

        return new_positions


    
