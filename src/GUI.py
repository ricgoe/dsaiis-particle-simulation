from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QGridLayout, QWidget, 
QPushButton, QHBoxLayout, QSlider, QLabel, QSizePolicy, QSpacerItem)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QScreen, QPalette
from matplotlib.pyplot import get_cmap
from Vispy_Stack import Canvas


from custom_widgets.Widgets import PopupWidget, CustomColorPicker, SquareWidget

PADDING = 5
SPLIT = 4
TICK_RATE = 20
CIRCLE_SION = 2
BORDER = 40
NPARTICLES = 5
RELATIONSHIPS = 10
MAX_PARTICLES = 750
MAX_PARTICLE_MASS = 10
MIN_PARTICLE_MASS = 1
MAX_PARTICLE_BOUNCINESS = 1
MAX_BOUNCINESS_STEPS = 100
SCALING_FACTOR = 0.77
COLOR_MAP = "viridis"
STEP_SIZE = 3          
                
class MainWindow(QMainWindow):
    """ Main window for the particle simulation """
    def __init__(self):
        """ Initialize the main window with settings and canvas
        
        Parameters
        ----------
            None
        """
        super().__init__()
        
        self.cmap = get_cmap(COLOR_MAP, RELATIONSHIPS+1) #Set color theme 
        self.color_distrubution = {}    #Dictionary to store color distribution for particles
        self.relationships = {}        #Dictionary to store relationships between particles
        
        self.setWindowTitle("Particle Simulation")
        self.setGeometry(100, 100, 1500, 800)   #Set window size
        self.setFixedSize(self.width(), self.height())  #Make window non-resizable
        self.setStyleSheet("background-color: #24242b;")    #Set background color
        
        container = QWidget()   #Initialize the container widget
        self.setCentralWidget(container)    #Set container as a central widget
        
        main_layout = QHBoxLayout(container)    #Initialize the main layout 

        ctrl_widget = QWidget()     #Initialize the widget to hold control elements
        ctrl_layout = QVBoxLayout(ctrl_widget, alignment=Qt.AlignTop)   #Initialize the layout for control elements
        main_layout.addWidget(ctrl_widget, 1)   #Add control widget to the main layout
        
        canvas_widget = QWidget()   #Initialize the widget to hold the canvas for particle simulation
        self.canvas_layout = QVBoxLayout(canvas_widget) 
        main_layout.addWidget(canvas_widget, SPLIT)   
        
        particle_widget = QWidget()    #Initialize the widget to hold particle color settings
        self.particle_layout = QVBoxLayout(particle_widget, alignment=Qt.AlignTop)
        ctrl_layout.addWidget(particle_widget)
        
        self.adder_btn = QPushButton("+", styleSheet="color: white; font-size: 20px; font-weight: bold; background-color: #31313a;") #Button to add particle class
        self.adder_btn.clicked.connect(self.add_particle_color)   #Connect button to add_particle_color method
        ctrl_layout.addWidget(self.adder_btn)   #Add button to layout with all controls
        
        rel_matrix = SquareWidget() #Widget to hold relationship matrix
        self.rel_layout = QGridLayout(rel_matrix)   
        self.rel_layout.setSpacing(3)  #Set spacing between elements in the layout
        ctrl_layout.addWidget(rel_matrix)
        
        ctrl_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding)) #Add spacer to push elements to the top
        
        self.save_btn = QPushButton("Save", styleSheet="color: white; font-size: 20px; background-color: #31313a;") #Button to save particle settings
        self.save_btn.hide()   #Hide the button until particle settings are added
        self.save_btn.clicked.connect(self.saved) #Connect button to saved-method
        ctrl_layout.addWidget(self.save_btn)
        
        self.reset_btn = QPushButton("Reset", styleSheet="color: white; font-size: 20px; background-color: #31313a;") #Button to reset particle settings
        self.reset_btn.hide()
        self.reset_btn.clicked.connect(self.reset)
        ctrl_layout.addWidget(self.reset_btn)
        
        refresh_rate = round(app.primaryScreen().refreshRate()) #Get user-screen refresh rate
        self.canvas = Canvas(bgcolor='#24242b', screen_refresh_rate=refresh_rate, particle_scaling_factor=SCALING_FACTOR) #Canvas to hold particle simulation
        self.canvas_layout.addWidget(self.canvas.native)
        
        self.show()
        
        
    
    def add_particle_color(self):
        """ Adds color settings for a new particle class:
            - Slider for number of particles
            - Color picker for particle color
        """
        if len(self.color_distrubution) < NPARTICLES:
            _c_widget = QWidget()
            _c_layout = QHBoxLayout(_c_widget)
            self.particle_layout.addWidget(_c_widget)
            
            btn = QPushButton(styleSheet="background-color: #ff0000;")
            color_box1 = QWidget(styleSheet="background-color: #ff0000;")
            color_box2 = QWidget(styleSheet="background-color: #ff0000;")
            color_box1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            color_box2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.color_distrubution[btn] = {"color": (1.0, 0, 0, 1.0), "n": int(MAX_PARTICLES//2), "mass": MIN_PARTICLE_MASS, "bounciness": float(MAX_PARTICLE_BOUNCINESS)}
            btn.clicked.connect(lambda: self.show_color_settings(btn, [color_box1, color_box2]))
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
                        rel_btn.clicked.connect(lambda _, i=i, j=j: self.show_relationship_slider(i, j))
                        self.rel_layout.addWidget(rel_btn, i, j)
                        entry = self.relationships.get((min(i, j), max(i, j)), { "button": [], "value": 0 })
                        entry["button"].append(rel_btn)
                        self.relationships[(min(i, j), max(i, j))] = entry
            if len(self.color_distrubution) == 1:
                self.save_btn.show()
                self.reset_btn.show()
            elif len(self.color_distrubution) >= NPARTICLES:
                self.adder_btn.hide()
                        
    
    def show_relationship_slider(self, i: int, j: int):
        """Opens a popup window with a slider to adjust the relationship between two particle classes
        
        Parameters
        ----------
        i : int
            First color index
        j : int
            Second color index 
            
        (i, j) describes the relationship between the ith and jth particle class
        """
        pop = PopupWidget(self)
        pop.setStyleSheet("background-color: #31313a;")
        lyt = QVBoxLayout(pop)
        label = QLabel(str(self.relationships[(min(i, j), max(i, j))]["value"]), styleSheet="color: white;", alignment=Qt.AlignCenter)
        slider = QSlider(Qt.Horizontal)
        slider.setRange(-int(RELATIONSHIPS/2), int(RELATIONSHIPS/2))
        slider.setValue(self.relationships[(min(i, j), max(i, j))]["value"])
        slider.valueChanged.connect(lambda val: self.relationship_slider_changed(val, label, i, j))
        lyt.addWidget(slider)
        lyt.addWidget(label)
        pop.show()
        
    def relationship_slider_changed(self, val, label: QLabel, i: int, j: int):
        """Callback function for relationship slider
        
        Parameters
        ----------
        val : int
            Slider value
        label : QLabel
            Label to display the slider value
        i : int
            First color index
        j : int
            Second color index
        """
        for btn in self.relationships[(min(i, j), max(i, j))]["button"]:
            btn.setStyleSheet(f"background-color: {self.get_cmap_color(val)}; margin: 0; padding: 0; border-radius: 0;")
        label.setText(str(val))
        self.relationships[(min(i, j), max(i, j))]["value"] = val
                
    def show_color_settings(self, btn: QPushButton, boxes=list[QWidget]):
        """Opens a popup window with color, mass and restitution setting for a particle class
        
        Parameters
        ----------
        btn : QPushButton
            Button that opened the popup window
        boxes : list[QWidget]
            Only passed to color_changed method
        """
        pop = PopupWidget(self)
        pop.setStyleSheet("background-color: #31313a;")
        lyt = QVBoxLayout(pop)
        cp = CustomColorPicker()
        cp.setCurrentColor(btn.palette().color(QPalette.Button))
        cp.currentColorChanged.connect(lambda color: self.color_changed(color, btn, boxes))
        lyt.addWidget(cp)
        mass_box = QWidget()
        mass_layout = QHBoxLayout(mass_box)
        mass_label = QLabel("Mass:         ", styleSheet="color: white;", alignment=Qt.AlignCenter)
        mass_val_label = QLabel(str(self.color_distrubution[btn]["mass"]), styleSheet="color: white;", alignment=Qt.AlignCenter)
        mass_slider = QSlider(Qt.Horizontal)
        mass_slider.setRange(MIN_PARTICLE_MASS, MAX_PARTICLE_MASS)
        mass_slider.setValue(self.color_distrubution[btn]["mass"])
        mass_slider.valueChanged.connect(lambda val: self.config_slider_changed(val, "mass", btn, mass_val_label))
        mass_layout.addWidget(mass_label)
        mass_layout.addWidget(mass_slider)
        mass_layout.addWidget(mass_val_label)
        bounciness_box = QWidget()
        bounciness_layout = QHBoxLayout(bounciness_box)
        bounciness_label = QLabel("Resitution:", styleSheet="color: white;", alignment=Qt.AlignCenter)
        bounciness_val_label = QLabel(str(self.color_distrubution[btn]["bounciness"]).ljust(4, "0"), styleSheet="color: white;", alignment=Qt.AlignCenter)
        bounciness_slider = QSlider(Qt.Horizontal)
        bounciness_slider.setRange(0, MAX_PARTICLE_BOUNCINESS*MAX_BOUNCINESS_STEPS)
        bounciness_slider.setValue(self.color_distrubution[btn]["bounciness"]*MAX_BOUNCINESS_STEPS)
        bounciness_slider.valueChanged.connect(lambda val: self.config_slider_changed(val/MAX_BOUNCINESS_STEPS, "bounciness", btn, bounciness_val_label))
        bounciness_layout.addWidget(bounciness_label)
        bounciness_layout.addWidget(bounciness_slider)
        bounciness_layout.addWidget(bounciness_val_label)
        lyt.addWidget(mass_box)
        lyt.addWidget(bounciness_box)
        pop.show()
        
    def color_changed(self, color: QColor, btn: QPushButton, boxes=list[QWidget]):
        """
        Callback function for color picker
        
        Parameters
        ----------
        btn : QPushButton
            Button to change color of
        boxes : list[QWidget]
            List of color boxes in relationship matrix to change color of
        """
        btn.setStyleSheet(f"background-color: {color.name()};")
        for i in boxes: i.setStyleSheet(f"background-color: {color.name()};")
        self.color_distrubution[btn]["color"] = tuple(x/255 for x in color.toTuple())
        
    def config_slider_changed(self, val:int|float, key: str, btn: QPushButton, label: QLabel):
        """Callback for mass and restitution sliders
        
        Parameters
        ----------
        val : int|float
            Slider value
        key : str ["mass", "bounciness"]
            Key to update in color_distrubution
        btn : QPushButton
            Only used as reference in color distribution
        label : QLabel
            Label to display the slider value
        """
        val_str = str(val) if isinstance(val, int) else str(val).ljust(4, "0")
        label.setText(str(val_str))
        self.color_distrubution[btn][key] = val

    def n_particle_slider_changed(self, val, label: QLabel, btn: QPushButton):
        """Callback function for number of particles slider

        Parameters
        ----------
        val : int
            Slider value
        label : QLabel
            Label to display the slider value
        btn : QPushButton
            Only used as reference in color distribution
        """
        label.setText(str(val))
        self.color_distrubution[btn]["n"] = val

    def get_cmap_color(self, idx):
        """Get color in hex-format from color map
        
        Parameters
        ----------
        idx : int
            Index of color in color map

        Returns
        -------
        str
            Hex color code
        """
        return QColor.fromRgbF(*self.cmap(int(RELATIONSHIPS/2)+idx)).name()
    
    def clear_layout(self, layout):
        """Clears a given layout of all widgets
        
        Parameters
        ----------
        layout : QLayout
            Layout to clear
        """
        while layout.count():  # While the layout has widgets
            child = layout.takeAt(0)  # Take the first item in the layout
            if child.widget():  # If it's a widget (not a nested layout or spacer)
                child.widget().deleteLater()  # Mark the widget for deletion
            elif child.layout():  # If it's a nested layout
                self.clear_layout(child.layout())  # Recursively clear the nested layout
    
    def saved(self):
        """Callback of save button
        
        Passes all the user settings to the VisPy Stack
"""
        _c_map = [[val["color"], val["n"], val["bounciness"], val["mass"]] for val in self.color_distrubution.values()]
        _r_map = {key : value["value"] for key, value in self.relationships.items()}
        self.canvas.insert_data(_c_map, _r_map) # load data
        
    def reset(self):
        """Callback of reset button

        Resets all user settings
        """
        self.color_distrubution = {}
        self.relationships = {}
        self.clear_layout(self.particle_layout)
        self.clear_layout(self.rel_layout)
        self.canvas.reset()
        self.adder_btn.show()
        self.save_btn.hide()
        self.reset_btn.hide()


if __name__ == "__main__":
    app = QApplication()
    window = MainWindow()
    window.show()
    app.exec()
    
