from vispy import app, scene
import numpy as np
from vispy.app import Timer
from particle_system import ParticleSystem
from collision_test import test_ParticleSystem



part_sys = test_ParticleSystem()
# part_sys = ParticleSystem(width=10000, height=10000, color_distribution=[((1, 0, 0, 1), 100000), ((0, 1, 0, 1), 100000)], step_size=.5, radius=.5)

canvas = scene.SceneCanvas(keys="interactive", show=True)
view = canvas.central_widget.add_view()

view.camera = scene.PanZoomCamera(aspect=1)
view.camera.set_range(x=(0, 100), y=(0, 100))


scatter = scene.visuals.Markers()
x, y = part_sys.particles[:,0], part_sys.particles[:,1]
scatter.set_data(np.array([x,y]).T, edge_color=part_sys.particles[:,2:], face_color=part_sys.particles[:,2:], size=part_sys.radius)
view.add(scatter)


def update(event):  
    part_sys.move_particles()
    x, y = part_sys.particles[:,0], part_sys.particles[:,1]
    scatter.set_data(np.array([x,y]).T, edge_color=part_sys.particles[:,2:], face_color=part_sys.particles[:,2:], size=part_sys.radius)
    
timer = Timer(interval=0.01, connect=update, start=True)

app.run()