import dearpygui.dearpygui as dpg
from part_wrapper import ParticleSystem

PADDING = 5
SPLIT = 6
TICK_RATE = 20


class GUI:
            
    def __init__(self):
        self.particle_system = ParticleSystem(width=1000, height=1000, color_distribution=[((255, 0, 0), 100)], step_size= 10)
        dpg.create_context()
        dpg.create_viewport()
        dpg.setup_dearpygui()
        # Add control panel
        with dpg.window(tag="exwin",label="Example Window", no_resize=True, no_move=True, no_collapse=True, no_close=True):
            dpg.add_text("Hello world")
            dpg.add_button(label="Save", callback=self.save_callback)
            dpg.add_input_text(label="string")
            dpg.add_slider_float(label="float")
        # Add particle simulation window
        with dpg.window(tag="exwin2",label="Example Window", no_resize=True, no_move=True, no_collapse=True, no_close=True):
            with dpg.drawlist(tag="exdrawlist", width=dpg.get_item_width("exwin2"), height=dpg.get_item_height("exwin2")) as self.drawlist:
                pass
            self.rendered_particles = self.render_particles()
        # Dymamic resize logic
        dpg.set_viewport_resize_callback(self.on_window_resize)
        dpg.set_frame_callback(20, self.tick)
        # Necessary run logic
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()
        
    
    def tick(self):
        frames = dpg.get_frame_count()
        next_tick_in = int(dpg.get_frame_rate()//TICK_RATE)
        self.particle_system.move_particles()
        self.render_movement()
        dpg.set_frame_callback(frames+next_tick_in, self.tick)
        
        
    def render_movement(self):
        for idx, rendered in enumerate(self.rendered_particles):
            dpg.set_item_pos(rendered, [self.particle_system.particles[idx].x_pos, self.particle_system.particles[idx].y_pos])
        
    def render_particles(self):
        return [dpg.draw_circle((particle.x_pos, particle.y_pos), 2, color=particle.color, parent=self.drawlist) for particle in self.particle_system.particles]

            
    
    def on_window_resize(self):
        dpg.set_item_width("exwin", dpg.get_viewport_width()//6)
        dpg.set_item_height("exwin", dpg.get_viewport_height())
        dpg.set_item_width("exwin2", dpg.get_viewport_width()-dpg.get_item_width("exwin")-PADDING)
        dpg.set_item_height("exwin2", dpg.get_viewport_height())
        dpg.set_item_pos("exwin2", (dpg.get_item_width("exwin")+PADDING,0))
        dpg.set_item_width("exdrawlist", dpg.get_item_width("exwin2"))
        dpg.set_item_height("exdrawlist", dpg.get_item_height("exwin2"))
        
        
    def save_callback(self):
        print("Save Clicked")
    def slider_callback(self, sender, app_data):
        print(app_data)
    
    
if __name__ == "__main__":
    GUI()