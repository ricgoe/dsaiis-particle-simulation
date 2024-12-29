from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QGridLayout, QWidget, 
QPushButton, QHBoxLayout, QSlider, QLabel, QSizePolicy, QSpacerItem)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
import re
from matplotlib.pyplot import get_cmap
from vispy_backend_stub import Canvas
from fake_data import POSITIONS, COLORS, PARTICLE_SIZE


from custom_widgets.widgets import PopupWidget, CustomColorPicker, SquareWidget

PADDING = 5
SPLIT = 4
TICK_RATE = 20
CIRCLE_SION = 2
BORDER = 40
NPARTICLES = 5
RELATIONSHIPS = 10
MAX_PARTICLES = 750
COLOR_MAP = "viridis"
STEP_SIZE = 3          
                
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.cmap = get_cmap(COLOR_MAP, RELATIONSHIPS+1)
        self.color_distrubution = {}
        self.relationships = {}
        
        self.setWindowTitle("Particle Simulation")
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
        self.rel_layout = QGridLayout(rel_matrix)
        self.rel_layout.setSpacing(3)
        ctrl_layout.addWidget(rel_matrix)
        
        ctrl_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding))
        
        self.save_btn = QPushButton("Save", styleSheet="color: white; font-size: 20px; background-color: #31313a;")
        self.save_btn.hide()
        self.save_btn.clicked.connect(self.saved)
        ctrl_layout.addWidget(self.save_btn)
        
        self.reset_btn = QPushButton("Reset", styleSheet="color: white; font-size: 20px; background-color: #31313a;")
        self.reset_btn.hide()
        self.reset_btn.clicked.connect(self.reset)
        ctrl_layout.addWidget(self.reset_btn)
        
        
        canvas = Canvas(bgcolor='#24242b') # EMIL
        canvas.insert_data(POSITIONS, COLORS, PARTICLE_SIZE) # load data
        self.canvas_layout.addWidget(canvas.native)
        
        self.show()
        
        
    
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
            btn.clicked.connect(lambda: self.show_color_picker(btn, [color_box1, color_box2]))
            _c_layout.addWidget(btn, 1)
            n = len(self.color_distrubution)
            self.rel_layout.addWidget(color_box1, n, 0)
            self.rel_layout.addWidget(color_box2, 0, n)
            
            label = QLabel(str(MAX_PARTICLES//2), styleSheet="color: white;")
            slider = QSlider(Qt.Horizontal)
            slider.setRange(1, MAX_PARTICLES)
            slider.setValue(MAX_PARTICLES//2)
            slider.valueChanged.connect(lambda val: self.n_particle_slider_changed(val, label, btn))
            _c_layout.addWidget(slider, SPLIT+1)
            _c_layout.addWidget(label, 1)
            for i in range(1, n+1):
                for j in range(1, n+1):
                    if i == n or j == n:
                        rel_btn = QPushButton(styleSheet=f"background-color: {self.get_cmap_color(0)}; margin: 0; padding: 0; border-radius: 0;")
                        rel_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                        rel_btn.clicked.connect(lambda _, btn=rel_btn, i=i, j=j: self.show_relationship_slider(btn, i, j))
                        self.rel_layout.addWidget(rel_btn, i, j)
                        self.relationships[(i, j)] = 0
            if len(self.color_distrubution) == 1:
                self.save_btn.show()
                self.reset_btn.show()
            elif len(self.color_distrubution) >= NPARTICLES:
                self.adder_btn.hide()
                        
    
    def show_relationship_slider(self, btn: QPushButton, i: int, j: int):
        pop = PopupWidget(self)
        pop.setStyleSheet("background-color: #31313a;")
        lyt = QVBoxLayout(pop)
        label = QLabel(str(self.relationships[(i, j)]), styleSheet="color: white;", alignment=Qt.AlignCenter)
        slider = QSlider(Qt.Horizontal)
        slider.setRange(-int(RELATIONSHIPS/2), int(RELATIONSHIPS/2))
        slider.setValue(self.relationships[(i, j)])
        slider.valueChanged.connect(lambda val: self.relationship_slider_changed(val, btn, label, i, j))
        lyt.addWidget(slider)
        lyt.addWidget(label)
        pop.show()
        
    def relationship_slider_changed(self, val, btn: QPushButton, label: QLabel, i: int, j: int):
        tmp_css = re.sub(r"background-color:\s*([^;]+)", f"background-color: {self.get_cmap_color(val)};", btn.styleSheet())
        btn.setStyleSheet(tmp_css)
        label.setText(str(val))
        self.relationships[(i, j)] = val
                
    def show_color_picker(self, btn: QPushButton, boxes=list[QWidget]):
        pop = PopupWidget(self)
        pop.setStyleSheet("background-color: #31313a;")
        lyt = QVBoxLayout(pop)
        cp = CustomColorPicker()
        _hex = re.match(r"background-color:\s*([^;]+)", btn.styleSheet()).group(1)
        cp.setCurrentColor(_hex)
        cp.currentColorChanged.connect(lambda color: self.color_changed(color, btn, boxes))
        lyt.addWidget(cp)
        pop.show()
        
    def color_changed(self, color: QColor, btn: QPushButton, boxes=list[QWidget]):
        btn.setStyleSheet(f"background-color: {color.name()};")
        for i in boxes: i.setStyleSheet(f"background-color: {color.name()};")
        self.color_distrubution[btn][0] = color.toTuple()
        
    def n_particle_slider_changed(self, val, label: QLabel, btn: QPushButton):
        label.setText(str(val))
        self.color_distrubution[btn][1] = val

    def get_cmap_color(self, idx):
        return QColor.fromRgbF(*self.cmap(int(RELATIONSHIPS/2)+idx)).name()
    
    def clear_layout(self, layout):
        while layout.count():  # While the layout has widgets
            child = layout.takeAt(0)  # Take the first item in the layout
            if child.widget():  # If it's a widget (not a nested layout or spacer)
                child.widget().deleteLater()  # Mark the widget for deletion
            elif child.layout():  # If it's a nested layout
                self.clear_layout(child.layout())  # Recursively clear the nested layout
    
    def saved(self):
        _c_map = list(self.color_distrubution.values())
        print(_c_map)
        print(self.relationships)
        
    def reset(self):
        self.color_distrubution = {}
        self.relationships = {}
        self.clear_layout(self.particle_layout)
        self.clear_layout(self.rel_layout)
        self.adder_btn.show()

        

if __name__ == "__main__":
    app = QApplication()
    window = MainWindow()
    window.show()
    app.exec()
    
