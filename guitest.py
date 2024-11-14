from vispy import app, scene
import numpy as np
from vispy.app import Timer
from particle_system import ParticleSystem



part_sys = ParticleSystem(width=100, height=100, color_distribution=[((1, 0, 0, 1), 100000), ((0, 1, 0, 1), 100000)], step_size=.5, radius=.5)

canvas = scene.SceneCanvas(keys="interactive", show=True)
view = canvas.central_widget.add_view()

view.camera = scene.PanZoomCamera(aspect=1)
view.camera.set_range(x=(0, 100), y=(0, 100))


scatter = scene.visuals.Markers()
x, y = part_sys.particles[:,0], part_sys.particles[:,1]
scatter.set_data(np.array([x,y]).T, edge_color=part_sys.particles[:,2:], face_color=part_sys.particles[:,2:])
view.add(scatter)


def update(event):  
    part_sys.move_particles()
    x, y = part_sys.particles[:,0], part_sys.particles[:,1]
    scatter.set_data(np.array([x,y]).T, edge_color=part_sys.particles[:,2:], face_color=part_sys.particles[:,2:])
    
timer = Timer(interval=0.05, connect=update, start=True)

app.run()