from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QGridLayout, QWidget, 
QPushButton, QHBoxLayout, QSlider, QLabel, QSizePolicy, QSpacerItem)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
import re


from custom_widgets.widgets import PopupWidget, CustomColorPicker, SquareWidget

PADDING = 5
SPLIT = 4
TICK_RATE = 20
CIRCLE_SION = 2
BORDER = 40
NPARTICLES = 5
RELATIONSHIPS = NPARTICLES*2
MAX_PARTICLES = 750
COLOR_MAP = "inferno"
STEP_SIZE = 3          
                
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.color_distrubution = {}
        
        self.setWindowTitle("Basic PySide6 GUI")
        self.setGeometry(100, 100, 1500, 800)
        self.setFixedSize(self.width(), self.height())
        self.setStyleSheet("background-color: #24242b;")
        
        container = QWidget()
        self.setCentralWidget(container)
        
        main_layout = QHBoxLayout(container)

        ctrl_widget = QWidget()
        ctrl_layout = QVBoxLayout(ctrl_widget, alignment=Qt.AlignTop)
        main_layout.addWidget(ctrl_widget, 1)
        
        canvas_widget = QWidget()
        self.canvas_layout = QVBoxLayout(canvas_widget)
        main_layout.addWidget(canvas_widget, SPLIT)
        
        particle_widget = QWidget()
        self.particle_layout = QVBoxLayout(particle_widget, alignment=Qt.AlignTop)
        ctrl_layout.addWidget(particle_widget)
        
        self.adder_btn = QPushButton("+", styleSheet="color: white; font-size: 20px; font-weight: bold; background-color: #31313a;")
        self.adder_btn.clicked.connect(self.add_particle_color)
        ctrl_layout.addWidget(self.adder_btn)
        
        rel_matrix = SquareWidget()
        # rel_matrix.setStyleSheet("background-color: #c29233;")
        self.rel_layout = QGridLayout(rel_matrix, )
        self.rel_layout.setContentsMargins(1,1,1,1)
        self.rel_layout.setSpacing(1)
        ctrl_layout.addWidget(rel_matrix)
        ctrl_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding))
    
    def add_particle_color(self):
        if len(self.color_distrubution) < NPARTICLES:
            _c_widget = QWidget()
            _c_layout = QHBoxLayout(_c_widget)
            self.particle_layout.addWidget(_c_widget)
            
            btn = QPushButton(styleSheet="background-color: #ff0000;")
            color_box1 = QWidget(styleSheet="background-color: #ff0000;")
            color_box2 = QWidget(styleSheet="background-color: #ff0000;")
            color_box1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            color_box2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.color_distrubution[btn] = [(255, 0, 0, 255), int(MAX_PARTICLES//2)]
            btn.clicked.connect(lambda: self.show_color_picker(btn, (color_box1, color_box2)))
            _c_layout.addWidget(btn, 1)
            n = len(self.color_distrubution)
            self.rel_layout.addWidget(color_box1, n, 0)
            self.rel_layout.addWidget(color_box2, 0, n)
            
            label = QLabel(str(MAX_PARTICLES//2), styleSheet="color: white;")
            slider = QSlider(Qt.Horizontal)
            slider.setRange(1, MAX_PARTICLES)
            slider.setValue(MAX_PARTICLES//2)
            slider.valueChanged.connect(lambda val: self.slider_changed(val, label, btn))
            _c_layout.addWidget(slider, SPLIT+1)
            _c_layout.addWidget(label, 1)
            for i in range(1, n+1):
                for j in range(1, n+1):
                    if i == n or j == n:
                        rel_btn = QPushButton(styleSheet="background-color: #36a840;")
                        rel_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                        self.rel_layout.addWidget(rel_btn, i, j)
            if len(self.color_distrubution) >= NPARTICLES:
                self.adder_btn.hide()
                        
            
    def show_color_picker(self, btn: QPushButton, boxes=tuple[QWidget]):
        pop = PopupWidget(self)
        pop.setStyleSheet("background-color: #31313a;")
        lyt = QVBoxLayout(pop)
        cp = CustomColorPicker()
        _hex = re.match(r"background-color:\s*([^;]+)", btn.styleSheet()).group(1)
        cp.setCurrentColor(_hex)
        cp.currentColorChanged.connect(lambda color: self.color_changed(color, btn))
        lyt.addWidget(cp)
        pop.show()
        
    def color_changed(self, color: QColor, btn: QPushButton, boxes=tuple[QWidget]):
        btn.setStyleSheet(f"background-color: {color.name()};")
        self.color_distrubution[btn][0] = color.toTuple()
        
    def slider_changed(self, val, label: QLabel, btn: QPushButton):
        label.setText(str(val))
        self.color_distrubution[btn][1] = val
        

if __name__ == "__main__":
    app = QApplication()
    window = MainWindow()
    window.show()
    app.exec()
    
