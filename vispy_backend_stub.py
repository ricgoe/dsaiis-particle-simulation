# from vispy import scene
# import numpy as np
# from vispy import app

# # Ensure VisPy uses the PySide6 backend
# app.use_app("pyside6")

# class Canvas(scene.SceneCanvas):
#     def __init__(self):
#         super().__init__(keys="interactive")
        
#         # self.unfreeze()
#         # Generate random x and y data
#         num_points = 100
#         x = np.random.rand(num_points)  # Random x values between 0 and 1
#         y = np.random.rand(num_points)  # Random y values between 0 and 1
#         positions = np.c_[x, y]

#         # Optional: Assign random colors and sizes to points
#         sizes = np.random.rand(num_points) * 100  # Random sizes between 0 and 100

#         view = self.central_widget.add_view()

#         view.camera = scene.PanZoomCamera(aspect=1)
#         view.camera.set_range(x=(0, 100), y=(0, 100))

#         scatter = scene.visuals.Markers()
#         scatter.set_data(positions, size=sizes, face_color=(1, 0, 0, 1))
#         view.add(scatter)
#         # self.freeze()

import numpy as np
from vispy import scene

class Canvas(scene.SceneCanvas):
    def __init__(self):
        super().__init__(keys="interactive", show=True, bgcolor='#24242b')#Hintergrundfarbe wie in PySide-GUI

        CANVAS_MARGIN_FACTOR = 0.05  # 5% Rand pro ohne Punkte

        view = self.central_widget.add_view()
        view.camera = scene.PanZoomCamera(aspect=1)

        # Datenerzeugung
        n_points = 100
        positions = np.random.rand(n_points, 2) * 10  # 2D array mit n_points vielen zufälligen Punkten, *10 um die Punkte auf dem Bildschirm zu verteilen
        colors = np.ones((n_points, 4))  # 4 weil rgba, letzter wert ist alpha, machen wir mal immer 1
        colors[:, :3] = np.random.rand(n_points, 3)  # rgb werte zufällig generieren

        # Um jedem Punkt auf Canvas sichtbar zu haben: Mini-und Maxima der x und y Werte bestimmen
        x_min, y_min = positions.min(axis=0)  # Minimum x und y
        x_max, y_max = positions.max(axis=0)  # Maximum x und y

        # Um die Kamera auf die Punkte zu zoomen: Streuweiten bestimmen und um 5% vergrößern
        x_range = x_max - x_min
        y_range = y_max - y_min
        x_margin = x_range * CANVAS_MARGIN_FACTOR
        y_margin = y_range * CANVAS_MARGIN_FACTOR

        view.camera.set_range(
            x=(x_min - x_margin, x_max + x_margin),
            y=(y_min - y_margin, y_max + y_margin)
        )

        # um die Punktgröße an das Canvas anzupassen
        # -> VisPy nimmt bei set_data die size nur in pixel an, nicht die relative Größe
        canvas_size = self.size  # Pixelgröße des Canvas
        canvas_relative_particle_size = min(canvas_size) * 0.02  # 2% der kleineren Dimension

        # scatter plot erstellen und daten übergeben
        scatter = scene.visuals.Markers()
        scatter.set_data(pos=positions, face_color=colors, size=canvas_relative_particle_size)
        view.add(scatter)
