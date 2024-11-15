import dearpygui.dearpygui as dpg
from part_wrapper import ParticleSystem

PADDING = 5
SPLIT = 5
TICK_RATE = 20
CIRCLE_SION = 2


class GUI:
            
    def __init__(self):
        dpg.create_context()
        dpg.create_viewport()
        dpg.setup_dearpygui()
        self.color_distrubution = {}
        self.should_stop = True
        # Add control panel
        with dpg.window(tag="exwin",label="Example Window", no_resize=True, no_move=True, no_collapse=True, no_close=True):
            with dpg.group(horizontal=True):
                btn1 = dpg.add_button(label="  ", callback=self.color_picker)
                dpg.add_slider_int(tag=f"btn_id:{btn1}", label="", callback=self.slider_callback, default_value=50)
                self.color_distrubution[btn1] = [(255, 0, 0, 255), 50]
            with dpg.group(horizontal=True):
                btn2 = dpg.add_button(label="  ", callback=self.color_picker)
                dpg.add_slider_int(tag=f"btn_id:{btn2}", label="", callback=self.slider_callback, default_value=50)
                self.color_distrubution[btn2] = [(255, 0, 0, 255), 50]
            with dpg.group(horizontal=True):
                btn3 = dpg.add_button(label="  ", callback=self.color_picker)
                dpg.add_slider_int(tag=f"btn_id:{btn3}", label="", callback=self.slider_callback, default_value=50)
                self.color_distrubution[btn3] = [(255, 0, 0, 255), 50]
            with dpg.theme() as btn_theme:
                with dpg.theme_component():
                    dpg.add_theme_color(dpg.mvThemeCol_Button, (255, 0, 0, 255))
            dpg.bind_item_theme(btn1, btn_theme)
            dpg.bind_item_theme(btn2, btn_theme)
            dpg.bind_item_theme(btn3, btn_theme)
            self.save = dpg.add_button(label="Save", callback=self.save_callback)
            self.pause = dpg.add_button(label="Pause", callback=self.pause_callback)
            self.reset = dpg.add_button(label="Stop", callback=self.stop_callback)
            
        dpg.hide_item(self.pause)
        dpg.hide_item(self.reset)
        
        
        self.particle_system = ParticleSystem(width=1000, height=1000, color_distribution=[((255, 0, 0), 100), ((255, 255, 0), 100), ((255, 22, 255), 100)], step_size=10)
        # Add particle simulation window
        with dpg.window(tag="exwin2",label="Example Window", no_resize=True, no_move=True, no_collapse=True, no_close=True):
            with dpg.drawlist(tag="exdrawlist", width=dpg.get_item_width("exwin2"), height=dpg.get_item_height("exwin2")) as self.drawlist:
                pass
        # Dymamic resize logic
        dpg.set_viewport_resize_callback(self.on_window_resize)
        # Necessary run logic
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()
    
    def slider_callback(self, sender, app_data):
        self.color_distrubution[int(dpg.get_item_alias(sender).split(":")[1])][1] = app_data
    
    def color_picker(self, btn, app_data):
        if dpg.does_item_exist(f"cp_popup_{btn}"):
            dpg.show_item(f"cp_popup_{btn}")
            return
        
        def cp_callback(cp, app_data):
            with dpg.theme() as btn_theme:
                with dpg.theme_component():
                    dpg.add_theme_color(dpg.mvThemeCol_Button, tuple([i*255 for i in app_data]))
            dpg.bind_item_theme(btn, btn_theme)
            self.color_distrubution[btn][0] = tuple([i*255 for i in app_data])

        pop = dpg.add_window(tag=f"cp_popup_{btn}", no_resize=True, no_move=True, no_collapse=True, no_close=True, popup=True)
        dpg.add_color_picker(tag=f"cp_{btn}", label="color picker", default_value=(255, 0, 0, 255), parent=pop, callback=cp_callback)
        
    
    
    def tick(self):
        if not self.should_stop:
            frames = dpg.get_frame_count()
            next_tick_in = int(dpg.get_frame_rate()//TICK_RATE)
            self.particle_system.move_particles()
            self.render_movement()
            dpg.set_frame_callback(frames+next_tick_in, self.tick)
        
        
    # def render_movement(self):
    #     print("render movement called")
        
    #     for idx, rendered in enumerate(self.rendered_particles):
    #         dpg.delete_item(rendered)
    #         dpg.draw_circle((self.particle_system.particles[idx].x_pos, self.particle_system.particles[idx].y_pos), CIRCLE_SION, color=self.particle_system.particles[idx].color, parent=self.drawlist)
    
    def clear_particles(self):
        for rendered in self.rendered_particles:
            dpg.delete_item(rendered)
        self.rendered_particles = []
    
    def render_movement(self):
        self.clear_particles()
        self.rendered_particles = self.render_particles()
    
    def render_particles(self):
        return [dpg.draw_circle((particle.x_pos, particle.y_pos), CIRCLE_SION, color=particle.color, parent=self.drawlist) for particle in self.particle_system.particles]

            
    
    def on_window_resize(self):
        dpg.set_item_width("exwin", dpg.get_viewport_width()//SPLIT)
        dpg.set_item_height("exwin", dpg.get_viewport_height())
        dpg.set_item_width("exwin2", dpg.get_viewport_width()-dpg.get_item_width("exwin")-PADDING)
        dpg.set_item_height("exwin2", dpg.get_viewport_height())
        dpg.set_item_pos("exwin2", (dpg.get_item_width("exwin")+PADDING,0))
        dpg.set_item_width("exdrawlist", dpg.get_item_width("exwin2"))
        dpg.set_item_height("exdrawlist", dpg.get_item_height("exwin2"))
        
    
    def pause_callback(self, btn, app_data):
        if not self.should_stop:
            self.should_stop = True
            dpg.configure_item(btn, label="Resume")
        else:
            self.should_stop = False
            self.tick() # Resume Loop
            dpg.configure_item(btn, label="Pause")
        
        
    
    def save_callback(self):
        _c_d_map = [tup for tup in self.color_distrubution.values()]
        self.particle_system = ParticleSystem(width=1000, height=1000, color_distribution=_c_d_map, step_size=10)
        self.rendered_particles = self.render_particles()
        self.should_stop = False
        self.tick()
        dpg.show_item(self.pause)
        dpg.show_item(self.reset)
        

        
    def stop_callback(self):
        self.should_stop = True
        self.clear_particles()
        dpg.hide_item(self.pause)
        dpg.hide_item(self.reset)

    
    
if __name__ == "__main__":
    GUI()