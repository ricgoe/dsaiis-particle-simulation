import numpy as np

class Particle:
    def __init__(self, color, x_pos, y_pos):
        self.color: tuple[int, int, int] = color
        self._x_pos: float = x_pos
        self._y_pos: float = y_pos
        
    @property
    def x_pos(self):
        return self._x_pos

    @x_pos.setter
    def x_pos(self, value):
        self._x_pos = value

    @property
    def y_pos(self):
        return self._y_pos

    @y_pos.setter
    def y_pos(self, new_value):
        self._y_pos = new_value
    
    def move(self, x_pos, y_pos):
        self.x_pos = x_pos
        self.y_pos = y_pos
        
if __name__ == "__main__":
    particle = Particle(color=(255, 0, 0), x_pos=0, y_pos=0)

    
    