import numpy as np
from vispy.app import run, Timer
from vispy import scene

CANVAS_MARGIN_FACTOR = 0.05  # 5% Rand pro ohne Punkte
PARTICLE_RADIUS = 5

canvas = scene.SceneCanvas(keys='interactive', show=True, bgcolor='#24242b') #Hintergrundfarbe wie in PySide-GUI

view = canvas.central_widget.add_view()
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
canvas_size = canvas.size  # Pixelgröße des Canvas
canvas_relative_particle_size = min(canvas_size) * 0.02  # 2% der kleineren Dimension

# scatter plot erstellen und daten übergeben
scatter = scene.visuals.Markers()
scatter.set_data(pos=positions, face_color=colors, size=canvas_relative_particle_size)
view.add(scatter)

#plot update
def update(ev):
    global positions, colors, canvas_relative_particle_size
    positions += np.random.randn(n_points, 2) * 0.01
    scatter.set_data(pos=positions, face_color=colors, size=canvas_relative_particle_size)
    canvas.update()

#timer
timer = Timer(interval=0.01) #1 Update pro hunderstel Sekunde
timer.connect(update)
timer.start()


if __name__ == '__main__':
    run()