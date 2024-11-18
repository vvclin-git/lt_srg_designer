import ctypes
import pygame
import pygame_gui
from Widgets import ZoomableCanvas, Polygon
from Widgets import TableWidget
import json
import numpy as np
# Set DPI awareness to bypass Windows scaling
ctypes.windll.user32.SetProcessDPIAware()

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

# Initialize pygame
pygame.init()

# Constants based on the schematic
WINDOW_WIDTH = 1800
WINDOW_HEIGHT = 1200
GAP = 10
SYSTEM_PARAMS_WIDTH = 400
DOE_PARAMS_PANEL_WIDTH = 1370
PARAMS_HEIGHT = 400
LAYOUT_WIDTH = 1270
KSPACE_MAP_WIDTH = 500

theme_path = '.\\Widgets\\theme.json'
with open('sys_params.json', 'r') as f:
    sys_params = json.load(f)

grating_types = ['ic', 'epe', 'oc']
grating_params_ic = []
grating_params_epe = []
grating_params_oc = []
grating_params = [grating_params_ic, grating_params_epe, grating_params_oc]

for i, t in enumerate(grating_types):
    with open(f'grating_params_{t}.json', 'r') as f:
        grating_params[i] = json.load(f)


# Set up the display
window_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('DOE Layout Designer')

# Set up the UI manager
manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT), theme_path=theme_path)

# Create UI Panels based on the schematic
system_parameters_panel = pygame_gui.elements.UIPanel(
    relative_rect=pygame.Rect((GAP, GAP), (SYSTEM_PARAMS_WIDTH, PARAMS_HEIGHT)),
    manager=manager,
    object_id='#system_parameters_panel'
)

system_parameters_label = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((10, 10), (SYSTEM_PARAMS_WIDTH - 2 * GAP, 30)),
    text='System Parameters',
    manager=manager,
    container=system_parameters_panel
)
sys_params_table_rect = pygame.Rect(system_parameters_label.rect.topleft[0], system_parameters_label.rect.topleft[1] + system_parameters_label.rect.height + GAP, SYSTEM_PARAMS_WIDTH - 2 * GAP, 300)
sys_params_table = TableWidget(sys_params_table_rect, manager, ['Parameters', 'Values'], sys_params, 0.55)

doe_parameters_panel = pygame_gui.elements.UIPanel(
    relative_rect=pygame.Rect((SYSTEM_PARAMS_WIDTH + 2 * GAP, GAP), (DOE_PARAMS_PANEL_WIDTH, PARAMS_HEIGHT)),
    manager=manager,
    object_id='#doe_parameters_panel'
)

doe_params_width = int((DOE_PARAMS_PANEL_WIDTH - 4 * GAP) / 3)
doe_parameters_label_1 = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((GAP, GAP), (doe_params_width, 30)),
    text='IC Parameters',
    manager=manager,
    container=doe_parameters_panel
)
doe_params_rect_1 = pygame.Rect(doe_parameters_label_1.rect.topleft[0], doe_parameters_label_1.rect.topleft[1] + system_parameters_label.rect.height + GAP, doe_params_width, PARAMS_HEIGHT)
grating_params_ic_table = TableWidget(doe_params_rect_1, manager, ['Parameters', 'Values'], grating_params[0], 0.55)

doe_parameters_label_2 = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((2 * GAP + doe_params_width, GAP), (doe_params_width, 30)),
    text='EPE Parameters',
    manager=manager,
    container=doe_parameters_panel
)
doe_params_rect_2 = pygame.Rect(doe_parameters_label_2.rect.topleft[0], doe_parameters_label_2.rect.topleft[1] + system_parameters_label.rect.height + GAP, doe_params_width, PARAMS_HEIGHT)
grating_params_epe_table = TableWidget(doe_params_rect_2, manager, ['Parameters', 'Values'], grating_params[1], 0.55)

doe_parameters_label_3 = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((3 * GAP + 2 * doe_params_width, GAP), (doe_params_width, 30)),
    text='OC Parameters',
    manager=manager,
    container=doe_parameters_panel
)
doe_params_rect_3 = pygame.Rect(doe_parameters_label_3.rect.topleft[0], doe_parameters_label_3.rect.topleft[1] + system_parameters_label.rect.height + GAP, doe_params_width, PARAMS_HEIGHT)
grating_params_oc_table = TableWidget(doe_params_rect_3, manager, ['Parameters', 'Values'], grating_params[2], 0.55)


k_space_map_panel = pygame_gui.elements.UIPanel(
    relative_rect=pygame.Rect((GAP, PARAMS_HEIGHT + 2 * GAP), (KSPACE_MAP_WIDTH, KSPACE_MAP_WIDTH + GAP + 30)),
    manager=manager,
    object_id='#k_space_map_panel'
)
k_space_map_label = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((GAP, GAP), (KSPACE_MAP_WIDTH - 2 * GAP, 30)),
    text='K-space Map',
    manager=manager,
    container=k_space_map_panel
)
k_space_rect = pygame.Rect(k_space_map_label.rect.topleft[0], k_space_map_label.rect.topleft[1] + k_space_map_label.rect.height + GAP, KSPACE_MAP_WIDTH - 2 * GAP, KSPACE_MAP_WIDTH - 2 * GAP)
init_kspace = Init_Kspace(1, 2)
k_space_canvas = ZoomableCanvas(window_surface, k_space_rect.x, k_space_rect.y, k_space_rect.width, k_space_rect.height, 520, 520, 'width', 100, init_kspace, px_to_kspace)

layout_view_panel = pygame_gui.elements.UIPanel(
    relative_rect=pygame.Rect((KSPACE_MAP_WIDTH + 2 * GAP, PARAMS_HEIGHT + 2 * GAP), (LAYOUT_WIDTH, WINDOW_HEIGHT - PARAMS_HEIGHT - 3 * GAP)),
    manager=manager,
    object_id='#layout_view_panel'
)

layout_view_label = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((GAP, GAP), (LAYOUT_WIDTH - 2 * GAP, 30)),
    text='Layout View',
    manager=manager,
    container=layout_view_panel
)

layout_view_rect = pygame.Rect(layout_view_label.rect.topleft[0], layout_view_label.rect.topleft[1] + layout_view_label.rect.height + GAP, LAYOUT_WIDTH - 2 * GAP, WINDOW_HEIGHT - PARAMS_HEIGHT - 3 * GAP)
layout_view_canvas = ZoomableCanvas(window_surface, layout_view_rect.x, layout_view_rect.y, layout_view_rect.width, layout_view_rect.height, 4000, 2000, 'width', 1000, px_to_coord=px_to_layout)

# Run the game loop
clock = pygame.time.Clock()

is_running = True
while is_running:
    time_delta = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False

        manager.process_events(event)

    manager.update(time_delta)

    window_surface.fill((255, 255, 255))
    k_space_canvas.handle_event(event)
    layout_view_canvas.handle_event(event)
    
    manager.draw_ui(window_surface)
    k_space_canvas.draw()
    layout_view_canvas.draw()
    pygame.display.update()

pygame.quit()
