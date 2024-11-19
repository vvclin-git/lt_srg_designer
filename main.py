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

class Polygon:
    def __init__(self, sides, size, center=(400, 300)):
        self.sides = sides
        self.size = size
        self.center = center
        self.vertices = self.create_polygon()
        self.control_pts = True
        self.control_pt_size = 5
    
    def __init__(self, vertices):        
        self.vertices = vertices
        self.control_pt_size = 5
        self.control_pts = True

    def create_polygon(self):
        """Create a regular polygon based on the number of sides and size."""
        angle_step = 2 * np.pi / self.sides
        return [(self.center[0] + self.size * np.cos(i * angle_step),
                 self.center[1] + self.size * np.sin(i * angle_step)) for i in range(self.sides)]
    
    def render(self, screen):
        """Draw the polygon and its vertices."""
        if self.vertices:
            pygame.draw.polygon(screen, (0, 0, 255), self.vertices, 2)  # Draw the polygon
            for vertex in self.vertices:
                pygame.draw.circle(screen, (255, 0, 0), (int(vertex[0]), int(vertex[1])), self.control_pt_size)  # Draw vertices as red dots
    
    def point_in_polygon(self, point):
        x, y = point
        polygon = self.vertices        
        n = len(polygon)
        inside = False
        p1x, p1y = polygon[0]
        for i in range(n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y

        return inside

    def update_vertex(self, index, new_position):
        """Update a specific vertex position."""
        self.vertices[index] = new_position
    
    def move_polygon(self, distance):
        for i in range(len(self.vertices)):            
            self.vertices[i] = (self.vertices[i][0] + distance[0], self.vertices[i][1] + distance[1])

    def get_closest_vertex(self, mouse_pos, threshold=10):
        """Find the closest vertex to the mouse position."""
        for index, vertex in enumerate(self.vertices):
            if np.linalg.norm(np.array(mouse_pos) - np.array(vertex)) < threshold:  # If close enough to the vertex
                return index
        return None

class KSpaceFOV(Polygon):    
    
    def __init__(self, kspace_canvas, center, hfov, vfov, angle_step, color):
        num = int((hfov / angle_step)) + 1
        hfov_pts = np.linspace(-0.5 * hfov, 0.5 * hfov, num)
        vfov_pts = np.linspace(-0.5 * vfov, 0.5 * vfov, num)
        vertices = self.get_outermost_points(hfov_pts, vfov_pts)
        vertices = self.angle_to_kspace(vertices)        
        center = np.array(center)
        vertices += center
        self.scale = kspace_canvas.scale
        vertices_px = vertices * kspace_canvas.scale
        vertices_px[:, 1] *= -1
        kspace_canvas_center = np.array([kspace_canvas.offset_x, kspace_canvas.offset_y])
        vertices_px += kspace_canvas_center
        super().__init__(vertices_px)
        self.color = color
    
    def angle_to_kspace(self, angle_coords):
        kspace_coords = np.zeros_like(angle_coords)
        angle_coords = np.radians(angle_coords)
        denom = np.sqrt(1 + np.power(angle_coords[:, 0], 2) + np.power(angle_coords[:, 1], 2))
        kspace_coords[:, 0] = np.tan(angle_coords[:, 0]) / denom
        kspace_coords[:, 1] = np.tan(angle_coords[:, 1]) / denom
        return kspace_coords
    
    def kspace_to_canvas(self, kspace_coords):
        return

    def get_outermost_points(self, x, y):        
        # Top and bottom rows (vary x, y fixed at min and max)
        top_bottom_x = np.concatenate([x, x])  # x varies
        top_bottom_y = np.concatenate([np.full_like(x, y[0]), np.full_like(x, y[-1])])  # y is fixed

        # Left and right columns (vary y, x fixed at min and max)
        left_right_x = np.concatenate([np.full_like(y[1:-1], x[0]), np.full_like(y[1:-1], x[-1])])  # x is fixed
        left_right_y = np.concatenate([y[1:-1], y[1:-1]])  # y varies

        # Combine all points
        outer_x = np.concatenate([top_bottom_x, left_right_x])
        outer_y = np.concatenate([top_bottom_y, left_right_y])

        # Combine into (x, y) pairs
        return np.column_stack((outer_x, outer_y))
    
    def get_closest_vertex(self, mouse_pos, threshold=10):
        pass

    def move_polygon(self, distance):
        for i in range(len(self.vertices)):            
            self.vertices[i] = (self.vertices[i][0] + distance[0], self.vertices[i][1] + distance[1])

    def render(self, screen):
        """Draw the polygon and its vertices."""
        if self.vertices is not None:
            pygame.draw.polygon(screen, self.color, self.vertices, 0)  # Draw the polygon
            # for vertex in self.vertices:
            #     pygame.draw.circle(screen, (255, 0, 0), (int(vertex[0]), int(vertex[1])), self.control_pt_size)  # Draw vertices as red dots

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

def init_fov(angle_steps, sys_params_table, grating_params_ic_table, grating_params_epe_table, grating_params_oc_table):
    hfov, vfov = [float(x) for x in sys_params_table.data_values[1].split('/')]
    fov_red_ic = KSpaceFOV(k_space_canvas, (0, 0), hfov, vfov, angle_steps, (255, 0, 0, 128))
    ic_grating_picth = float(grating_params_ic_table.data_values[0])
    ic_grating_vector_angle = float(grating_params_ic_table.data_values[1])
    red_shift_x_ic, red_shift_y_ic = 
    
    fov_red_epe = KSpaceFOV(k_space_canvas, (red_shift_x_ic, red_shift_y_ic), hfov, vfov, angle_steps, (255, 0, 0, 128))
    fov_red_oc = KSpaceFOV(k_space_canvas, (red_shift_x_epe, red_shift_y_epe), hfov, vfov, angle_steps, (255, 0, 0, 128))
    fov_green_ic = KSpaceFOV(k_space_canvas, (0, 0), hfov, vfov, angle_steps, (0, 255, 0, 128))
    
    fov_green_epe = KSpaceFOV(k_space_canvas, (green_shift_x_ic, green_shift_y_ic), hfov, vfov, angle_steps, (255, 0, 0, 128))
    fov_green_oc = KSpaceFOV(k_space_canvas, (green_shift_x_epe, green_shift_y_epe), hfov, vfov, angle_steps, (255, 0, 0, 128))
    
    fov_blue_ic = KSpaceFOV(k_space_canvas, (0, 0), hfov, vfov, angle_steps, (0, 0, 255, 128))
    
    fov_blue_epe = KSpaceFOV(k_space_canvas, (blue_shift_x_ic, blue_shift_y_ic), hfov, vfov, angle_steps, (255, 0, 0, 128))
    fov_blue_oc = KSpaceFOV(k_space_canvas, (blue_shift_x_epe, blue_shift_y_epe), hfov, vfov, angle_steps, (255, 0, 0, 128))
    return


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
    sys_params_table.handle_event(event)
    grating_params_ic_table.handle_event(event)
    grating_params_epe_table.handle_event(event)
    grating_params_oc_table.handle_event(event)

    manager.draw_ui(window_surface)
    k_space_canvas.draw()
    layout_view_canvas.draw()
    pygame.display.update()

pygame.quit()
