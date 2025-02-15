from vispy import scene, app
import numpy as np
from particle_system import ParticleSystem


class Canvas(scene.SceneCanvas):
    def __init__(self, bgcolor, screen_refresh_rate=60):
        super().__init__(keys='interactive', bgcolor=bgcolor)
        self.unfreeze()  # Allow addition of new attributes
        self.CANVAS_MARGIN_FACTOR = 0.05  # 5% Rand pro ohne Punkte
        self.particle_scaling_factor = 0.001  # Skalierungsfaktor für Partikelgrößen
        self.view = self.central_widget.add_view()
        self.view.camera = scene.PanZoomCamera(aspect=1)
        self.scatter = scene.visuals.Markers(scaling = 'scene')
        self.part_sys = None
        self.update_interval = 1 / screen_refresh_rate
        self.timer = app.Timer(interval=self.update_interval, connect=self.update_positions)

    def insert_data(self, color_distribution, interaction_matrix):
        self.part_sys = ParticleSystem(self.native.width(), self.native.height(), color_distribution, interaction_matrix)
        
        self.positions = self.part_sys.positions
        self.colors = self.part_sys.colors
        self.sizes = self.part_sys.size

        x_min, y_min = self.positions.min(axis=0)
        x_max, y_max = self.positions.max(axis=0)
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
        self.scatter.set_data(pos=self.positions, face_color=self.colors, edge_color=self.colors, size=self.relative_particle_sizes)
        self.view.camera.zoom(0.55)
        self.view.camera.center=(self.native.width()//2, self.native.height()//2)
        self.view.add(self.scatter)

        # Timer für Updates
        self.timer.start()

    def update_positions(self, ev):
        self.part_sys.move_particles()
        self.positions = self.part_sys.positions
        self.scatter.set_data(pos=self.positions, face_color=self.colors, edge_color=self.colors, size=self.relative_particle_sizes)
        self.update()
        
    def reset(self):
        self.timer.stop()
        self.scatter.parent = None