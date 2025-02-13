from matplotlib import pyplot as plt
from particle_system import ParticleSystem
import numpy as np
from matplotlib.patches import Circle

FPS = 20
part_sys = ParticleSystem(width=10, height=10, color_distribution=[((1, 0, 0), 2)], radius=1, interaction_matrix={(1, 1): 1})
part_sys.particles = np.array([[1, 1], [7, 1]])
plt.ion()
fig, ax = plt.subplots()
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
while True:
    # Remove previous circles by clearing the axis
    ax.clear()
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    
    # Draw each particle as a circle with a radius of 3 data units
    for pos in part_sys.positions:
        circle = Circle((pos[0], pos[1]), radius=part_sys.radius, color='red')
        ax.add_patch(circle)
    
    part_sys.move_particles()
    plt.pause(1 / FPS)
