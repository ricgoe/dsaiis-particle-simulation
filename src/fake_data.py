import numpy as np

n_points = 1000

def get_positions(): 
    positions = np.random.rand(n_points, 2) * 15  # 2D array mit n_points vielen zufälligen Punkten, *15 um die Punkte auf dem Bildschirm zu verteilen
    return positions

def get_colors():
    colors = np.ones((n_points, 4))  # 4 weil rgba, letzter wert ist alpha, machen wir mal immer 1
    colors[:, :3] = np.random.rand(n_points, 3)  # rgb werte zufällig generieren    
    return colors

def get_particle_size():
    #ganzzahlige Partikelgrößen erzeugen
    #particle_size = np.ones((n_points,)) * 10
    particle_size = np.random.randint(low=10, high=25,size=(n_points,)) # braucht INTs da Werte Pixelanzahl beschreiben
    return particle_size

