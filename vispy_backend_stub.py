from vispy import scene, app
import numpy as np

class Canvas(scene.SceneCanvas):
    def __init__(self):
        super().__init__(keys='interactive', show=True, bgcolor='#24242b')  # Hintergrundfarbe wie in PySide-GUI
        self.unfreeze()  # Allow addition of new attributes
        self.CANVAS_MARGIN_FACTOR = 0.05  # 5% Rand pro ohne Punkte
        self.particle_scaling_factor = 0.001  # Skalierungsfaktor für Partikelgrößen
        self.view = self.central_widget.add_view()
        self.view.camera = scene.PanZoomCamera(aspect=1)
        self.scatter = scene.visuals.Markers()
        self.update_interval = 0.01  # 1 Update pro hunderstel Sekunde -> 100Hz
        self.timer = app.Timer(interval=self.update_interval, connect=self.update_positions)

    def insert_data(self, positions, colors, sizes):
        self.positions = positions
        self.colors = colors
        self.sizes = sizes

        x_min, y_min = positions.min(axis=0)
        x_max, y_max = positions.max(axis=0)
        x_range = x_max - x_min
        y_range = y_max - y_min
        x_margin = x_range * self.CANVAS_MARGIN_FACTOR
        y_margin = y_range * self.CANVAS_MARGIN_FACTOR

        self.view.camera.set_range(
            x=(x_min - x_margin, x_max + x_margin),
            y=(y_min - y_margin, y_max + y_margin)
        )

        # Punktgrößen relativ zur Canvas-Größe skalieren
        canvas_size = self.size # Canvas-größe in Pixeln  (Breite, Höhe)
        scale_factor = min(canvas_size) * self.particle_scaling_factor # Skalierungsfaktor für Partikelgrößen
        self.relative_particle_sizes = np.array(self.sizes) * scale_factor # wird an Scatterplot übergeben 

        # Scatter-Plot hinzufügen
        self.scatter.set_data(pos=self.positions, face_color=self.colors, size=self.relative_particle_sizes)
        self.view.add(self.scatter)

        # Timer für Updates
        self.timer.start()

    def update_positions(self, ev):
        self.positions += np.random.randn(*self.positions.shape) * 0.01
        self.scatter.set_data(pos=self.positions, face_color=self.colors, size=self.relative_particle_sizes)
        self.update()