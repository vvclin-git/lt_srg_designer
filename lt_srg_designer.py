
import numpy as np
import pygame
import pygame_gui
from Widgets import ZoomableCanvas, Polygon, CANVAS_MODIFIED_EVENT
from Widgets import TableWidget, KSpaceFOV
import json


WINDOW_WIDTH = 1800
WINDOW_HEIGHT = 1200
GAP = 10
SYSTEM_PARAMS_WIDTH = 400
DOE_PARAMS_PANEL_WIDTH = 1370
PARAMS_HEIGHT = 400
LAYOUT_WIDTH = 1270
KSPACE_MAP_WIDTH = 500

# helper functions

# pixel coordinate conversion helper functions
def px_to_kspace(self, px_coords):
    canvas_center = np.array([self.offset_x, self.offset_y])
    canvas_pos = np.array([self.x, self.y])
    kspace_coord = np.zeros_like(px_coords)
    kspace_coord = px_coords - canvas_pos - canvas_center
    kspace_coord = kspace_coord / self.scale
    kspace_coord[1] = kspace_coord[1] * -1 
    return kspace_coord

def px_to_layout(self, px_coords):
    canvas_center = np.array([self.offset_x, self.offset_y])
    canvas_pos = np.array([self.x, self.y])
    layout_coord = np.zeros_like(px_coords)
    layout_coord = px_coords - canvas_pos - canvas_center
    layout_coord = layout_coord / self.scale
    layout_coord[1] = layout_coord[1] * -1
    return layout_coord

def parse_float_vals(input, delimiter):
        input_vals = input.split(delimiter)
        parsed_vals = []
        for v in input_vals:
            parsed_vals.append(float(v))
        return parsed_vals

def sys_params_calc(self):                    
    hfov, vfov = parse_float_vals(self.data_values[1], '/')
    dfov = np.sqrt(hfov ** 2 + vfov ** 2)
    self.data_values[2] = f'{dfov:0.4f}'
    pass



class Init_Kspace:
    def __init__(self, n1, n2) -> None:            
        self.n1 = n1
        self.n2 = n2
        pass
    def draw_kspace_circles(self, canvas, n1, n2):        
        bg_color=(255, 255, 255) 
        canvas.canvas_surface.fill(bg_color)
        origin_x, origin_y = int(canvas.canvas_surface.width / 2), int(canvas.canvas_surface.height / 2)
        pygame.draw.circle(canvas.canvas_surface, (0, 0, 0), (origin_x, origin_y), n1 * canvas.scale, 2)            
        pygame.draw.circle(canvas.canvas_surface, (0, 0, 0), (origin_x, origin_y), n2 * canvas.scale, 2)
        return        
    def __call__(self, instance):
        """Invoke the wrapped function with the given instance and stored parameters"""
        print('init k-space plot')
        self.draw_kspace_circles(instance, self.n1, self.n2)    
    def update(self, connected_table):
        self.n1 = float(connected_table.data_values[7])
        self.n2 = float(connected_table.data_values[6])


class DOE:
    def __init__(self, fov_in, fov_out, grating_table, sys_params_table, kspace_canvas, doe_before=None, doe_after=None) -> None:
        self.fov_in = fov_in
        self.fov_out = fov_out
        self.grating_table = grating_table
        self.system_params_table = sys_params_table
        self.kspace_canvas = kspace_canvas
        self.doe_before = doe_before
        self.doe_after = doe_after
        pass
    
    def calculate_angle(self, start, end):        
        # Calculate the vector components
        vector = np.array(end) - np.array(start)        
        # Calculate the angle in radians relative to the positive y-axis
        angle_radians = np.arctan2(vector[1], vector[0])  # y first, x second        
        # Convert the angle to degrees
        angle_degrees = np.degrees(angle_radians)
        if angle_degrees > 180:
            angle_degrees -= 360        
        # Normalize the angle to the range [0, 360)
        return angle_degrees
    
    def handle_event(self, event):
         # Handle all pygame.USEREVENTs dynamically
        if event.type in [pygame_gui.UI_BUTTON_PRESSED, pygame_gui.UI_DROP_DOWN_MENU_CHANGED, pygame_gui.UI_HORIZONTAL_SLIDER_MOVED, pygame_gui.UI_TEXT_ENTRY_FINISHED]:
            if 'ui_element' in event.__dict__ and event.ui_element in self.grating_table.data_value_fields:
                object_id = event.__dict__['ui_object_id'].split('.')
                if 'params' in object_id:
                    self.update_fov()
                    if self.doe_before is not None:                        
                        self.doe_before.update_grating()
                    # if self.doe_after is not None:
                    #     self.doe_after.update_fov()
                if 'grating' in object_id:
                    # if event.ui_element in self.grating_table.data_value_fields:
                        self.update_next_fov()
                        self.doe_after.update_grating()
                # Handle Group A events
                # if object_id.startswith("params"):
                #     self.update_fov()
        elif event.type == CANVAS_MODIFIED_EVENT:
            self.update_grating()

    def update_grating(self):
        print('update grating parameters')
        self.grating_table.data_values[0] = f'{self.fov_in.wavelength / np.linalg.norm(self.fov_out.center - self.fov_in.center):0.4f}'
        self.grating_table.data_values[1] = f'{self.fov_in.center[0]:0.4f}, {self.fov_in.center[1]:0.4f}'
        self.grating_table.data_values[2] = f'{self.calculate_angle(self.fov_in.center, self.fov_out.center):0.4f}'
        self.grating_table.update()
    
    def parse_float_vals(self, input, delimiter):
        input_vals = input.split(delimiter)
        parsed_vals = []
        for v in input_vals:
            parsed_vals.append(float(v))
        return parsed_vals

    def update_fov(self):        
        hfov, vfov = self.parse_float_vals(self.system_params_table.data_values[1], '/')        
        center = self.parse_float_vals(self.grating_table.data_values[1], ',')
        self.fov_in.update_vertices(center, hfov, vfov)
        self.kspace_canvas.update_canvas()
        print('update fov locations')
    
    def update_next_fov(self):
        center = self.parse_float_vals(self.grating_table.data_values[1], ',')
        print(f'fov center before {center}, ', end='')
        grating_pitch = float(self.grating_table.data_values[0])
        grating_angle = float(self.grating_table.data_values[2])
        center += np.array([self.fov_in.wavelength / grating_pitch * np.cos(np.radians(grating_angle)), self.fov_in.wavelength / grating_pitch * np.sin(np.radians(grating_angle))])
        print(f'fove center after {center}, grating pitch:{grating_pitch}, grating_angle:{grating_angle}')
        self.doe_after.fov_in.center = center
        self.doe_after.grating_table.data_values[1] = f'{center[0]:0.4f}, {center[1]:0.4f}'
        self.doe_after.update_fov()
        




class LT_SRG_Designer:
    def __init__(self, window_surface, manager, sys_params, grating_params) -> None:
        self.window_surface = window_surface
        self.manager = manager
        self.sys_params = sys_params
        self.grating_params = grating_params
        self.init_kspace = Init_Kspace(float(self.sys_params[7]['value']), float(self.sys_params[6]['value']))
        self.widgets = []
        self.init_widget()
        
        fov_red_ic, fov_red_epe, fov_red_oc = self.init_fov(30, 30, 0.1, [(0, 0), (1.5, 0), (0, -1.5)])
        self.k_space_canvas.add_shape(fov_red_ic)
        self.k_space_canvas.add_shape(fov_red_epe)
        self.k_space_canvas.add_shape(fov_red_oc)
        doe_1 = DOE(fov_red_ic, fov_red_epe, self.grating_params_ic_table, self.sys_params_table, self.k_space_canvas)
        doe_2 = DOE(fov_red_epe, fov_red_oc, self.grating_params_epe_table, self.sys_params_table, self.k_space_canvas)
        doe_3 = DOE(fov_red_oc, fov_red_ic, self.grating_params_oc_table, self.sys_params_table, self.k_space_canvas)

        doe_1.doe_before = doe_3
        doe_1.doe_after = doe_2
        doe_2.doe_before = doe_1
        doe_2.doe_after = doe_3
        doe_3.doe_before = doe_2
        doe_3.doe_after = doe_1

        self.does = [doe_1, doe_2, doe_3]

        pass
    
    def init_fov(self, hfov, vfov, angle_steps, centers):

        fov_red_ic = KSpaceFOV(self.k_space_canvas, centers[0], hfov, vfov, angle_steps, (255, 0, 0, 128))
        fov_red_epe = KSpaceFOV(self.k_space_canvas, centers[1], hfov, vfov, angle_steps, (255, 0, 0, 128))
        fov_red_oc = KSpaceFOV(self.k_space_canvas, centers[2], hfov, vfov, angle_steps, (255, 0, 0, 128))
        
        # fov_green_ic = KSpaceFOV(k_space_canvas, (0, 0), hfov, vfov, angle_steps, (0, 255, 0, 128))    
        # fov_green_epe = KSpaceFOV(k_space_canvas, (green_shift_x_ic, green_shift_y_ic), hfov, vfov, angle_steps, (255, 0, 0, 128))
        # fov_green_oc = KSpaceFOV(k_space_canvas, (green_shift_x_epe, green_shift_y_epe), hfov, vfov, angle_steps, (255, 0, 0, 128))
        
        # fov_blue_ic = KSpaceFOV(k_space_canvas, (0, 0), hfov, vfov, angle_steps, (0, 0, 255, 128))    
        # fov_blue_epe = KSpaceFOV(k_space_canvas, (blue_shift_x_ic, blue_shift_y_ic), hfov, vfov, angle_steps, (255, 0, 0, 128))
        # fov_blue_oc = KSpaceFOV(k_space_canvas, (blue_shift_x_epe, blue_shift_y_epe), hfov, vfov, angle_steps, (255, 0, 0, 128))
        return fov_red_ic, fov_red_epe, fov_red_oc
    
    def init_widget(self):
        # Create UI Panels based on the schematic
        system_parameters_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((GAP, GAP), (SYSTEM_PARAMS_WIDTH, PARAMS_HEIGHT)),
            manager=self.manager,
            object_id='#system_parameters_panel'
        )

        system_parameters_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((GAP, GAP), (SYSTEM_PARAMS_WIDTH - 2 * GAP, 30)),
            text='System Parameters',
            manager=self.manager,
            container=system_parameters_panel
        )
        sys_params_table_rect = pygame.Rect(system_parameters_label.rect.topleft[0], system_parameters_label.rect.topleft[1] + system_parameters_label.rect.height + GAP, SYSTEM_PARAMS_WIDTH - 2 * GAP, 300)
        self.sys_params_table = TableWidget(sys_params_table_rect, self.manager, ['Parameters', 'Values'], self.sys_params, 0.55, object_id='params', calc_func=sys_params_calc, connected_objs=[self.init_kspace])
        self.widgets.append(self.sys_params_table)
        doe_parameters_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((SYSTEM_PARAMS_WIDTH + 2 * GAP, GAP), (DOE_PARAMS_PANEL_WIDTH, PARAMS_HEIGHT)),
            manager=self.manager,
            object_id='#doe_parameters_panel'
        )

        doe_params_width = int((DOE_PARAMS_PANEL_WIDTH - 4 * GAP) / 3)
        doe_parameters_label_1 = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((GAP, GAP), (doe_params_width, 30)),
            text='IC Parameters',
            manager=self.manager,
            container=doe_parameters_panel
        )
        doe_params_rect_1 = pygame.Rect(doe_parameters_label_1.rect.topleft[0], doe_parameters_label_1.rect.topleft[1] + system_parameters_label.rect.height + GAP, doe_params_width, PARAMS_HEIGHT)
        self.grating_params_ic_table = TableWidget(doe_params_rect_1, self.manager, ['Parameters', 'Values'], self.grating_params[0], 0.55, object_id='params')
        self.grating_params_ic_table.data_value_fields[0].change_object_id('grating')
        self.widgets.append(self.grating_params_ic_table)
        doe_parameters_label_2 = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((2 * GAP + doe_params_width, GAP), (doe_params_width, 30)),
            text='EPE Parameters',
            manager=self.manager,
            container=doe_parameters_panel
        )
        doe_params_rect_2 = pygame.Rect(doe_parameters_label_2.rect.topleft[0], doe_parameters_label_2.rect.topleft[1] + system_parameters_label.rect.height + GAP, doe_params_width, PARAMS_HEIGHT)
        self.grating_params_epe_table = TableWidget(doe_params_rect_2, self.manager, ['Parameters', 'Values'], self.grating_params[1], 0.55, object_id='params')
        self.grating_params_epe_table.data_value_fields[0].change_object_id('grating')
        self.widgets.append(self.grating_params_epe_table)
        doe_parameters_label_3 = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((3 * GAP + 2 * doe_params_width, GAP), (doe_params_width, 30)),
            text='OC Parameters',
            manager=self.manager,
            container=doe_parameters_panel
        )
        doe_params_rect_3 = pygame.Rect(doe_parameters_label_3.rect.topleft[0], doe_parameters_label_3.rect.topleft[1] + system_parameters_label.rect.height + GAP, doe_params_width, PARAMS_HEIGHT)
        self.grating_params_oc_table = TableWidget(doe_params_rect_3, self.manager, ['Parameters', 'Values'], self.grating_params[2], 0.55, object_id='params')
        self.grating_params_oc_table.data_value_fields[0].change_object_id('grating')
        self.widgets.append(self.grating_params_oc_table)
        k_space_map_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((GAP, PARAMS_HEIGHT + 2 * GAP), (KSPACE_MAP_WIDTH, KSPACE_MAP_WIDTH + GAP + 30)),
            manager=self.manager,
            object_id='#k_space_map_panel'
        )
        k_space_map_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((GAP, GAP), (KSPACE_MAP_WIDTH - 2 * GAP, 30)),
            text='K-space Map',
            manager=self.manager,
            container=k_space_map_panel
        )
        k_space_rect = pygame.Rect(k_space_map_label.rect.topleft[0], k_space_map_label.rect.topleft[1] + k_space_map_label.rect.height + GAP, KSPACE_MAP_WIDTH - 2 * GAP, KSPACE_MAP_WIDTH - 2 * GAP)
        self.k_space_canvas = ZoomableCanvas(self.window_surface, k_space_rect.x, k_space_rect.y, k_space_rect.width, k_space_rect.height, 800, 800, 200, self.init_kspace, px_to_kspace, object_id='canvas')
        self.widgets.append(self.k_space_canvas)

        layout_view_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((KSPACE_MAP_WIDTH + 2 * GAP, PARAMS_HEIGHT + 2 * GAP), (LAYOUT_WIDTH, WINDOW_HEIGHT - PARAMS_HEIGHT - 3 * GAP)),
            manager=self.manager,
            object_id='#layout_view_panel'
        )

        layout_view_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((GAP, GAP), (LAYOUT_WIDTH - 2 * GAP, 30)),
            text='Layout View',
            manager=self.manager,
            container=layout_view_panel
        )
        # layout_view_rect = pygame.Rect(layout_view_label.rect.topleft[0], layout_view_label.rect.topleft[1] + layout_view_label.rect.height + GAP, LAYOUT_WIDTH - 2 * GAP, WINDOW_HEIGHT - PARAMS_HEIGHT - 3 * GAP)
        layout_view_rect = pygame.Rect(layout_view_label.rect.topleft[0], layout_view_label.rect.topleft[1] + layout_view_label.rect.height + GAP, LAYOUT_WIDTH - 2 * GAP, layout_view_panel.rect.height - layout_view_label.rect.height - 3 * GAP)
        self.layout_view_canvas = ZoomableCanvas(self.window_surface, layout_view_rect.x, layout_view_rect.y, layout_view_rect.width, layout_view_rect.height, 4000, 2000, 1000, px_to_coord=px_to_layout)
        self.widgets.append(self.layout_view_canvas)
        pass

    def handle_event(self, event):
        for w in self.widgets:
            w.handle_event(event)
        for d in self.does:
            d.handle_event(event)
        pass
    
    def draw(self):
        self.k_space_canvas.draw()
        self.layout_view_canvas.draw()