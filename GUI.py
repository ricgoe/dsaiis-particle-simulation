import dearpygui.dearpygui as dpg
from part_wrapper import ParticleSystem
from matplotlib.pyplot import get_cmap

PADDING = 5
SPLIT = 5
TICK_RATE = 20
CIRCLE_SION = 3
BORDER = 40
NPARTICLES = 5
RELATIONSHIPS = NPARTICLES*2
MAX_PARTICLES = 10000
COLOR_MAP = "inferno"


class GUI:
            
    def __init__(self):
        dpg.create_context()
        dpg.create_viewport()
        dpg.setup_dearpygui()
        self.particle_system = None
        self.color_distrubution = {}
        self.color_relationships = {}
        self.matrix_btns = []
        self.should_stop = True
        self.hovered_matrix = ""
        self.cmap = get_cmap(COLOR_MAP, RELATIONSHIPS+1)
        # Add control panel
        with dpg.window(tag="exwin",label="Example Window", no_resize=True, no_move=True, no_collapse=True, no_close=True):
            self.adder = dpg.add_button(label="+", callback=self.add_particle_picker)
            self.save = dpg.add_button(label="Save", callback=self.save_callback)
            self.pause = dpg.add_button(label="Pause", callback=self.pause_callback)
            self.reset = dpg.add_button(label="Stop", callback=self.stop_callback)
            with dpg.drawlist(tag="matrix", width=0, height=0):
                pass
            self.add_particle_picker()
            
        dpg.hide_item(self.pause)
        dpg.hide_item(self.reset)
        
        # Add particle simulation window
        with dpg.window(tag="exwin2", label="Example Window", no_resize=True, no_move=True, no_collapse=True, no_close=True):
            with dpg.drawlist(tag="particle_canvas", width=0, height=0):
                pass
        with dpg.handler_registry():
            dpg.add_mouse_move_handler(callback=self.hover_callback)
            dpg.add_mouse_click_handler(callback=self.click_callback)
                
        # Dymamic resize logic
        dpg.set_viewport_resize_callback(self.on_window_resize)
        # Necessary run logic
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()
        
        
    def add_particle_picker(self):
        if len(self.color_distrubution) < NPARTICLES:
            with dpg.group(horizontal=True, before=self.adder):
                btn = dpg.add_button(label="  ", callback=self.color_picker)
                dpg.add_slider_int(tag=f"btn_id:{btn}", label="", callback=self.slider_callback, default_value=int(MAX_PARTICLES/2), max_value=MAX_PARTICLES, min_value=1)
                self.color_distrubution[btn] = [(255, 0, 0, 255), int(MAX_PARTICLES/2)]
            with dpg.theme() as btn_theme:
                with dpg.theme_component():
                    dpg.add_theme_color(dpg.mvThemeCol_Button, (255, 0, 0, 255))
            dpg.bind_item_theme(btn, btn_theme)
            self.adjust_matrix(btn)
            if len(self.color_distrubution) >= NPARTICLES:
                dpg.hide_item(self.adder)
            
            
    def adjust_matrix(self, btn):
        _c_map = [tup[0] for tup in self.color_distrubution.values()]
        n = len(_c_map)
        w_h = 25 # TODO: Make this dynamic
        color = _c_map[-1]
        self.color_relationships[n] = {}
        h = dpg.draw_rectangle((n*w_h, 0), ((n+1)*w_h, w_h), tag= f"h_matrix_{btn}", fill=color, color=(100, 100, 100, 255), parent="matrix")
        v = dpg.draw_rectangle((0, n*w_h), (w_h, (n+1)*w_h), tag= f"v_matrix_{btn}", fill=color,  color=(100, 100, 100, 255), parent="matrix")
        for i in range(1, n+1):
            for j in range(1, n+1):
                if i == n or j == n:
                    dpg.draw_rectangle((i*w_h, j*w_h), ((i+1)*w_h, (j+1)*w_h), fill=self.get_cmap_color(int(RELATIONSHIPS/2)), color=(70, 70, 70, 255), parent="matrix", tag=f"matrix_{i}_{j}")
                    self.color_relationships[i][j] = 0
                    self.color_relationships[j][i] = 0
    
    def get_cmap_color(self, idx):
        
        rgba_convert = tuple([c*255 for c in self.cmap(idx)])
        return rgba_convert
    
    def slider_callback(self, sender, app_data):
        self.color_distrubution[int(dpg.get_item_alias(sender).split(":")[1])][1] = app_data
    
    
    def color_picker(self, btn, app_data):
        if dpg.does_item_exist(f"cp_popup_{btn}"):
            dpg.show_item(f"cp_popup_{btn}")
            return
        
        
        def cp_callback(cp, app_data):
            c = tuple([i*255 for i in app_data])
            with dpg.theme() as btn_theme:
                with dpg.theme_component():
                    dpg.add_theme_color(dpg.mvThemeCol_Button, c)
            dpg.bind_item_theme(btn, btn_theme)
            self.color_distrubution[btn][0] = c
            dpg.configure_item(f"h_matrix_{btn}", fill=c)
            dpg.configure_item(f"v_matrix_{btn}", fill=c)

        pop = dpg.add_window(tag=f"cp_popup_{btn}", no_resize=True, no_move=True, no_collapse=True, no_close=True, popup=True)
        dpg.add_color_picker(tag=f"cp_{btn}", label="color picker", default_value=(255, 0, 0, 255), parent=pop, callback=cp_callback)
        
    
    def on_matrix_hover(self, sender):
        self.hovered_matrix = sender
        dpg.configure_item(sender, color=(255, 255, 255, 255))
        
        
    def click_callback(self):
        if self.hovered_matrix:
            m, c1, c2 = self.hovered_matrix.split("_")
            sorted_label = f"{m}_{max(c1, c2)}_{min(c1, c2)}"
            if dpg.does_item_exist(f"{sorted_label}_popup"):
                dpg.show_item(f"{sorted_label}_popup")
                return
            pop = dpg.add_window(tag=f"{sorted_label}_popup", no_resize=True, no_move=True, no_collapse=True, no_close=True, popup=True, min_size=(0,0))
            dpg.add_slider_int(tag=f"{sorted_label}_slider", parent=pop, max_value=int(RELATIONSHIPS/2), min_value=-int(RELATIONSHIPS/2), callback=self.relationship_slider_callback)
    
    
    def hover_callback(self, sender, app_data):
        if self.hovered_matrix:
            dpg.configure_item(self.hovered_matrix, color=(70, 70, 70, 255))
            self.hovered_matrix = ""
        from_x, from_y = dpg.get_item_rect_min("matrix")
        to_x, to_y = dpg.get_item_rect_max("matrix")
        if to_x > app_data[0] > from_x and to_y > app_data[1] > from_y:
            n_colors = len(self.color_distrubution)
            for i in range(1, n_colors+1):
                for j in range(1, n_colors+1):
                    from_m_x, from_m_y = dpg.get_item_configuration(f"matrix_{i}_{j}")["pmin"]
                    to_m_x, to_m_y = dpg.get_item_configuration(f"matrix_{i}_{j}")["pmax"]
                    if from_x+to_m_x > app_data[0] > from_x+from_m_x and from_y+to_m_y > app_data[1] > from_y+from_m_y:
                        self.on_matrix_hover(f"matrix_{i}_{j}")
                        # dpg.set_frame_callback(callback=self.on_matrix_hover, sender=f"matrix_{i}_{j}")
        # print(dpg.get_item_configuration("matrix_2_2")) # pmax pmin
    
    
    def tick(self):
        if not self.should_stop:
            self.particle_system.move_particles()
            self.render_movement()
            frames = dpg.get_frame_count()
            next_tick_in = int(dpg.get_frame_rate()//TICK_RATE)
            dpg.set_frame_callback(frames+next_tick_in, self.tick)
        
        
    def render_movement(self):
        for idx, rendered in enumerate(self.rendered_particles):
            dpg.configure_item(rendered, center=(self.particle_system.particles[idx].x_pos, self.particle_system.particles[idx].y_pos))
            
            
    def clear_particles(self):
        for rendered in self.rendered_particles:
            dpg.delete_item(rendered)
        self.rendered_particles = []
        
        
    def render_particles(self):
        return [dpg.draw_circle((particle.x_pos, particle.y_pos), CIRCLE_SION, color=particle.color, parent="particle_canvas", fill=particle.color) for particle in self.particle_system.particles]


    def relationship_slider_callback(self, slider, app_data):
        _, c1, c2, _ = dpg.get_item_alias(slider).split("_")
        c_idx = app_data+int(RELATIONSHIPS/2)
        self.color_relationships[int(c1)][int(c2)] = app_data
        self.color_relationships[int(c2)][int(c1)] = app_data
        dpg.configure_item(f"matrix_{c1}_{c2}", fill=self.get_cmap_color(c_idx))
        dpg.configure_item(f"matrix_{c2}_{c1}", fill=self.get_cmap_color(c_idx))
    
    
    def on_window_resize(self):
        dpg.set_item_width("exwin", dpg.get_viewport_width()//SPLIT)
        dpg.set_item_height("exwin", dpg.get_viewport_height())
        dpg.set_item_width("exwin2", dpg.get_viewport_width()-dpg.get_item_width("exwin")-PADDING)
        dpg.set_item_height("exwin2", dpg.get_viewport_height())
        dpg.set_item_pos("exwin2", (dpg.get_item_width("exwin")+PADDING,0))
        dpg.set_item_width("particle_canvas", dpg.get_item_width("exwin2"))
        dpg.set_item_height("particle_canvas", dpg.get_item_height("exwin2")-BORDER)
        dpg.set_item_width("matrix", dpg.get_item_width("exwin")-PADDING*2)
        dpg.set_item_height("matrix", dpg.get_item_width("exwin")-PADDING*2)
        if self.particle_system:
            self.particle_system.width = dpg.get_item_width("particle_canvas")
            self.particle_system.height = dpg.get_item_height("particle_canvas")
        
        
    
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
        print(self.color_relationships) # handle appropriatly
        self.particle_system = ParticleSystem(width=dpg.get_item_width("particle_canvas"), height=dpg.get_item_width("particle_canvas"), color_distribution=_c_d_map, step_size=1)
        self.rendered_particles = self.render_particles()
        self.should_stop = False
        self.tick()
        dpg.hide_item(self.save)
        dpg.show_item(self.pause)
        dpg.show_item(self.reset)
        
        
    def stop_callback(self):
        self.should_stop = True
        self.clear_particles()
        dpg.hide_item(self.pause)
        dpg.hide_item(self.reset)
        dpg.show_item(self.save)

if __name__ == "__main__":
    GUI()