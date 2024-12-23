from vispy import scene
import numpy as np
from vispy import app

# Ensure VisPy uses the PySide6 backend
app.use_app("pyside6")

class Canvas(scene.SceneCanvas):
    def __init__(self):
        super().__init__(keys="interactive")
        
        self.unfreeze()
        # Generate random x and y data
        num_points = 100
        x = np.random.rand(num_points)  # Random x values between 0 and 1
        y = np.random.rand(num_points)  # Random y values between 0 and 1
        positions = np.c_[x, y]

        # Optional: Assign random colors and sizes to points
        sizes = np.random.rand(num_points) * 100  # Random sizes between 0 and 100

        view = self.central_widget.add_view()

        view.camera = scene.PanZoomCamera(aspect=1)
        view.camera.set_range(x=(0, 100), y=(0, 100))

        scatter = scene.visuals.Markers()
        scatter.set_data(positions, size=sizes, face_color=(1, 0, 0, 1))
        view.add(scatter)
        self.freeze()