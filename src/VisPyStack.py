from vispy import scene, app
import numpy as np
from ParticleSystem import ParticleSystem

class Canvas(scene.SceneCanvas):
    """ Class for creating a canvas to display a particle system using VisPy """

    def __init__(self, bgcolor: str, screen_refresh_rate: int=60, particle_scaling_factor: float=0.70):
        """
        Initialize the Canvas object

        Parameters
        ----------
        bgcolor : str
            Background color of the canvas, accepts hex color codes
        screen_refresh_rate : int, optional
            Refresh rate of the screen in Hz, by default set to 60Hz
        particle_scaling_factor : float, optional
            Scaling factor for particle sizes, by default 0.001
        """
        super().__init__(keys='interactive', bgcolor=bgcolor)
        self.unfreeze()  #Allow addition of new attributes
        self.particle_scaling_factor = particle_scaling_factor 
        self.view = self.central_widget.add_view()
        self.view.camera = scene.PanZoomCamera(aspect=1.2)    #Camera allows interactive pan and zoom to inspect the particle system 
        self.scatter = scene.visuals.Markers(scaling="scene") #To correctly display particle sizes with respect to current zoom level
        self.part_sys = None    #Placeholder for particle system
        self.update_interval = 1 / screen_refresh_rate      #To transfer screen_refresh_rate to Hz
        self.timer = app.Timer(interval=self.update_interval, connect=self.update_positions)    #Timer to update particle positions

    def insert_data(self, color_distribution: dict, interaction_matrix: dict):
        """
        Insert data into the particle system and scatter plot

        Parameters
        ----------
        color_distribution : dict
            Dictionary with color distribution for particles
        interaction_matrix : np.ndarray
            Matrix like dict to define interactions between particle-types

        """
        #initialize particle system
        self.part_sys = ParticleSystem(self.native.width(), self.native.height(), color_distribution, interaction_matrix, radius=1, delta_t = self.update_interval)
        
        #extract particle system attributes
        self.positions = self.part_sys.positions
        self.colors = self.part_sys.colors
        self.sizes = self.part_sys.size * self.particle_scaling_factor

        #prepare camera settings
        x_min, y_min = self.positions.min(axis=0)   #get min values for x and y columns
        x_max, y_max = self.positions.max(axis=0)   #get max values for x and y columns

        #Set camera range to cover all particles
        self.view.camera.set_range(
            x=(x_min, x_max),
            y=(y_min, y_max)
        )

        #Apply scaling factor to particle sizes

        #Add particles to canvas
        self.scatter.set_data(pos=self.positions, face_color=self.colors, edge_color=self.colors, size=self.sizes)
        self.view.camera.zoom(0.80) #Set intial zoom level to cover full canvas
        self.view.camera.center=(self.native.width()//2, self.native.height()//2)   #Center the camera to middle of canvas
        self.view.add(self.scatter) #Add scatter plot to view to be displayed

        #Timer for updates
        self.timer.start()

    def update_positions(self, _ev):
        """
        Update particle positions and colors
        
        Parameters
        ----------
        ev : Event
            An unused event object
        """
        self.part_sys.move_particles()  #call method to update particle positions
        self.positions = self.part_sys.positions    #grab updated positions
        self.scatter.set_data(pos=self.positions, face_color=self.colors, edge_color=self.colors, size=self.sizes)    
        self.update()   #update the canvas
        
    def reset(self):
        """
        Reset the particle system and view
        """
        self.timer.stop()   
        self.scatter.parent = None  #remove scatter plot from view
        
if __name__ == '__main__':
    rel = {(1, 1): {'value': 0}, (1, 2): {'value': 2}, (2, 1): {'value': -2}, (2, 2): {'value': 1}, (1, 3): {'value': -2}, (2, 3): {'value': 2}, (3, 1): {'value': 0}, (3, 2): {'value': -2}, (3, 3): {'value': 1}}
    color_distrubution = {
        "key0": {
            "color": (0.2, 0.6, 0, 1.0),
            "n": 375,
            "mass": 1,
            "bounciness": 1.0,
        },
        "key1": {
            "color": (0.2, 0.4, 0.6, 1.0),
            "n": 375,
            "mass": 1,
            "bounciness": 1.0,
        },
        "key2": {
            "color": (0.9, 0.1, 0.1, 1.0),
            "n": 375,
            "mass": 1,
            "bounciness": 1.0,
        },
    }
    canvas = Canvas(bgcolor='#24242b')
    canvas.show(True)
    canvas.fullscreen = True
    canvas.insert_data(color_distrubution, rel)
    app.run()
    
    
    
