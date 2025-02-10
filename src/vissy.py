from vispy import app, scene
import numpy as np
from vispy.app import Timer
from particle_system import ParticleSystem

class DummyVisualizer:
    def __init__(self, canvas_width, canvas_height, num_parts, fps):
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.num_parts = num_parts
        self.sim_width = 10
        self.sim_height = 10
        self.sim_radius = 1
        self.fps = fps
        self.interval = 1/self.fps
        
        self.part_sys = ParticleSystem(
            width=self.sim_width,
            height=self.sim_height,
            color_distribution=[
                ((1, 0, 0), int(self.num_parts/2)),  
                ((0, 0, 1), int(self.num_parts/2))
            ],
            radius=self.sim_radius,
            delta_t= self.interval
        )

        # mapping from color indices to RGBA (workaround)
        self.color_map = np.array([
            [1, 0, 0, 1],
            [0, 1, 0, 1]
        ])

        self.particle_colors = self.color_map[self.part_sys.particles[:, 5].astype(int)]


    def create_canvas(self):
        self.canvas = scene.SceneCanvas(keys="interactive", show=True, size=(self.canvas_width, self.canvas_height))
        self.view = self.canvas.central_widget.add_view()

        # set up camera.
        self.view.camera = scene.PanZoomCamera(aspect=self.sim_width / self.sim_height)
        self.view.camera.set_range(x=(0, self.sim_width), y=(0, self.sim_height))
        
        # create scatter visual
        self.pixel_radius = self.compute_pixel_radius()
        self.scatter = scene.visuals.Markers()
        x, y = self.part_sys.particles[:, 0], self.part_sys.particles[:, 1]
        self.scatter.set_data(
            np.column_stack((x, y)),
            edge_color=self.particle_colors,
            face_color=self.particle_colors,
            size=self.pixel_radius  # size in pixels
        )
        self.view.add(self.scatter)
            
            
            
    def compute_pixel_radius(self):
        """
        Compute the conversion factor from simulation units to pixels.

        """
        # conversion factor from simulation units to pixels
        conversion_factor = self.canvas_width / self.sim_width
        pixel_radius = self.sim_radius * conversion_factor
        
        return pixel_radius


    def update(self, event):
        """
        Update function to move particles and update scatter data.
        """
        self.part_sys.move_particles()
        x, y = self.part_sys.particles[:, 0], self.part_sys.particles[:, 1]
        self.scatter.set_data(
            np.column_stack((x, y)),
            edge_color=self.particle_colors,
            face_color=self.particle_colors,
            size=self.pixel_radius
        )


if __name__ == "__main__":
    vissy = DummyVisualizer(canvas_width=1000, canvas_height=1000, num_parts=4, fps=30)
    vissy.create_canvas()
    timer = Timer(vissy.interval, connect=vissy.update, start=True)
    app.run()