from vispy import app, scene
import numpy as np
from vispy.app import Timer
from particle_system import ParticleSystem

part_sys = ParticleSystem(width=20, height=20, color_distribution=[((1, 0, 0, 1), 100000), ((0, 1, 0, 1), 100000)], step_size=.5, radius=20, override = True)

canvas = scene.SceneCanvas(keys="interactive", show=True)
view = canvas.central_widget.add_view()

view.camera = scene.PanZoomCamera(aspect=1)
view.camera.set_range(x=(0, 100), y=(0, 100))

scatter = scene.visuals.Markers()
x, y = part_sys.particles[:,2], part_sys.particles[:,3]
scatter.set_data(np.array([x,y]).T, edge_color=[0,1,0,1], face_color=[0,1,0,1], size=part_sys.radius)
view.add(scatter)


def update(event):  
    part_sys.move_controlled()
    # print(part_sys.calc_col_force_arr(k = 10, collision_arr = part_sys.check_collision()))
    part_sys.calc_collsion_movement(k=20)
    x, y = part_sys.particles[:,2], part_sys.particles[:,3]
    scatter.set_data(np.array([x,y]).T, edge_color=[1,0,0,1], face_color=[0,1,0,1], size=part_sys.radius)
    
timer = Timer(interval=0.2, connect=update, start=True)

app.run()