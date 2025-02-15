from matplotlib import pyplot as plt
from particle_system import ParticleSystem
import numpy as np
from matplotlib.patches import Circle, Ellipse

FPS = 10
part_sys = ParticleSystem(width=100, height=50, color_distribution=[((1, 0, 0), 2, 1, 1)], radius=10, interaction_matrix={(1, 1): 100})
part_sys._particles = np.array([[10, 5], [30, 5]])
part_sys._velocity = np.array([[0, .25], [0, .25]]).astype(float)
part_sys._interaction_matrix = {(1, 1): 0}
plt.ion()
fig, ax = plt.subplots()
ax.axis('equal')
ax.set_xlim(0, 100)
ax.set_ylim(0, 50)
while True:
    # Remove previous circles by clearing the axis
    ax.clear()
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 50)
    
    # Draw each particle as a circle with a radius of 3 data units
    for pos in part_sys.positions:
        ellipsis = Ellipse((pos[0], pos[1]), width=part_sys.radius*2, height=part_sys.radius*2, angle=0, color='red')
        ax.add_patch(ellipsis)
    
    part_sys.move_particles()
    plt.pause(1 / FPS)
    
