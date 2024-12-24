import numpy as np

n_points = 1000
positions = np.random.rand(n_points, 2) * 10  # 2D array mit n_points vielen zufälligen Punkten, *10 um die Punkte auf dem Bildschirm zu verteilen
colors = np.ones((n_points, 4))  # 4 weil rgba, letzter wert ist alpha, machen wir mal immer 1
colors[:, :3] = np.random.rand(n_points, 3)  # rgb werte zufällig generieren

#ganzzahlige Partikelgrößen erzeugen
particle_size = np.random.randint(low=10, high=25,size=(n_points,)) # braucht INTs da Werte Pixelanzahl beschreiben

#particle_size = np.ones((n_points,)) * 10

POSITIONS = positions
COLORS = colors
PARTICLE_SIZE = particle_size