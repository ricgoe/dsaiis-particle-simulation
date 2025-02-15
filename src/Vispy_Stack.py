from vispy import scene, app
import numpy as np
from particle_system import ParticleSystem


class Canvas(scene.SceneCanvas):
    """ Class for creating a canvas to display a particle system using VisPy """

    def __init__(self, bgcolor: str, screen_refresh_rate: int=60, particle_scaling_factor: float=0.001):
        """
        Initialize the Canvas object

        Parameters
        ----------
        bgcolor : str
            Background color of the canvas, accepts hex color codes
        screen_refresh_rate : int, optional
            Refresh rate of the screen in Hz, by default set to 60Hz
        canvas_margin_factor : float, optional
            Margin factor for the canvas, by default 0.05 -> 5% margin between particles and canvas border
        particle_scaling_factor : float, optional
            Scaling factor for particle sizes, by default 0.001
        """
        super().__init__(keys='interactive', bgcolor=bgcolor)
        self.unfreeze()  #Allow addition of new attributes
        self.particle_scaling_factor = particle_scaling_factor 
        self.view = self.central_widget.add_view()
        self.view.camera = scene.PanZoomCamera(aspect=1.2)    #Allows interactive pan and zoom to inspect the particle system 
        self.scatter = scene.visuals.Markers(scaling = 'scene') #To correctly display particle sizes with respect to current zoom level
        self.part_sys = None    #Placeholder for particle system
        self.update_interval = 1 / screen_refresh_rate      #To transfer screen_refresh_rate to Hz
        self.timer = app.Timer(interval=self.update_interval, connect=self.update_positions)    #Timer to update particle positions

    def insert_data(self, color_distribution: dict, interaction_matrix: np.ndarray):
        """
        Insert data into the particle system and scatter plot

        Parameters
        ----------
        color_distribution : dict
            Dictionary with color distribution for particles
        interaction_matrix : np.ndarray

        """
        #initialize particle system
        self.part_sys = ParticleSystem(self.native.width(), self.native.height(), color_distribution, interaction_matrix)
        
        #extract particle system attributes
        self.positions = self.part_sys.positions
        self.colors = self.part_sys.colors
        self.sizes = self.part_sys.size

        #prepare camera settings
        x_min, y_min = self.positions.min(axis=0)   #get min values for x and y columns
        x_max, y_max = self.positions.max(axis=0)   #get max values for x and y columns

        #Set camera range to cover all particles
        self.view.camera.set_range(
            x=(x_min, x_max),
            y=(y_min, y_max)
        )

        #Apply scaling factor to particle sizes
        self.relative_particle_sizes = np.array(self.sizes) * self.particle_scaling_factor #to be given to the scatter plot

        #Add particles to canvas
        self.scatter.set_data(pos=self.positions, face_color=self.colors, edge_color=self.colors, size=self.relative_particle_sizes)
        self.view.camera.zoom(0.65) #Set intial zoom level to cover full canvas
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
        self.scatter.set_data(pos=self.positions, face_color=self.colors, edge_color=self.colors, size=self.relative_particle_sizes)    
        self.update()   #update the canvas
        
    def reset(self):
        """
        Reset the particle system and view
        """
        self.timer.stop()   
        self.scatter.parent = None  #remove scatter plot from view