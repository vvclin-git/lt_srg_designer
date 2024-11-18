import pygame
import pygame_gui
from pygame import gfxdraw
import sys
import numpy as np
import ast
from functools import partial

WHITE = (255, 255, 255)
BLACK = (0, 0, 0) 
BLUE = (0, 0, 255, 50)
RED = (255, 0, 0, 50)
GREY_D = (100, 100, 100)
GREY_L = (200, 200, 200)

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

class ZoomableCanvas:
    def __init__(self, parent_surface, x, y, width, height, canvas_width, canvas_height, init_zoom_fit='height', scale=1, init_canvas=None, px_to_coord=None, shapes=[]):
        self.parent_surface = parent_surface
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.shapes = shapes
        self.scale = scale
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        if init_canvas is not None:
            self.initialize_canvas = lambda: init_canvas(self)
        else:
            self.initialize_canvas = self.default_initialize_canvas
        
        if px_to_coord is not None:
            self.px_to_coord = px_to_coord
        else:
            self.px_to_coord = lambda self, px_coord: px_coord
        
        # Create a canvas surface
        self.canvas_surface = pygame.Surface((canvas_width, canvas_height), pygame.SRCALPHA)
        
        self.initialize_canvas()       

        # Zoom and pan variables
        if init_zoom_fit == 'height':
            self.init_zoom = height / canvas_height
        elif init_zoom_fit == 'width':
            self.init_zoom = width / canvas_width
        self.zoom = self.init_zoom
        self.offset_x, self.offset_y = int(canvas_width * 0.5), int(canvas_height * 0.5)
        self.panning = False
        self.moving_polygon = False
        self.resizing_polygon = False
        self.selected_polygon = None
        self.dragging_vertex = None
        self.drag_start = (self.offset_x, self.offset_y)        


    def default_initialize_canvas(self):
        grid_size = 100
        bg_color=(255, 255, 255)
        # Initialize canvas with background color, grid, and border
        self.canvas_surface.fill(bg_color)
        pygame.draw.rect(self.canvas_surface, BLACK, pygame.Rect(0, 0, self.canvas_width, self.canvas_height), 2)
        # if self.grid:
        canvas_dimension = np.array([self.canvas_width, self.canvas_height])
        grid_line_num = np.array([int(self.canvas_width / grid_size) + 1, int(self.canvas_height / grid_size) + 1])
        grid_line_start_pos = ((canvas_dimension - (grid_line_num - 1) * grid_size) * 0.5).astype(int)
        for i in range(grid_line_num[0]):
            pygame.draw.line(self.canvas_surface, BLACK, (grid_line_start_pos[0] + i * grid_size, 0), (grid_line_start_pos[0] + i * grid_size, canvas_dimension[1]), width=2)
        for j in range(grid_line_num[1]):
            pygame.draw.line(self.canvas_surface, BLACK, (0, grid_line_start_pos[1] + j * grid_size), (canvas_dimension[0], grid_line_start_pos[1] + j * grid_size), width=2)
            
    
    def in_canvas(self, pos):
        if self.x <= pos[0] <= self.x + self.width and self.y <= pos[1] <= self.y + self.height:
            return True
        return False


    def handle_event(self, event):
        if self.in_canvas(pygame.mouse.get_pos()):
            print(self.px_to_coord(self, pygame.mouse.get_pos()))
            if event.type == pygame.MOUSEWHEEL:
                old_zoom = self.zoom
                if event.y > 0:  # Zoom in
                    self.zoom *= 1.1                
                elif event.y < 0:  # Zoom out
                    if  int(self.width / self.zoom * 1.1) > self.canvas_surface.get_width() and int(self.height / self.zoom * 1.1) > self.canvas_surface.get_height():
                        self.zoom = self.width / self.canvas_surface.get_width()
                    else:
                        self.zoom /= 1.1

                # print(f'zoom level {self.zoom} view area dimension: {int(self.width / self.zoom)}x{int(self.height / self.zoom)}, canvas dimension: {self.canvas_surface.get_width()}x{self.canvas_surface.get_height()}')
                # Limit zoom to reasonable levels
                self.zoom = max(self.init_zoom, min(self.zoom, 5.0))

                mouse_x, mouse_y = pygame.mouse.get_pos()
                print(f'zoom level:{self.zoom}, mouse location: {mouse_x, mouse_y}')
                rel_x = (mouse_x - self.x - self.offset_x) / old_zoom
                rel_y = (mouse_y - self.y - self.offset_y) / old_zoom
                self.offset_x = mouse_x - self.x - rel_x * self.zoom
                self.offset_y = mouse_y - self.y - rel_y * self.zoom

                # Ensure offset stays within bounds after zooming
                self.offset_x = min(max(self.offset_x, -(self.canvas_surface.get_width() * self.zoom - self.width) / self.zoom), 0)
                self.offset_y = min(max(self.offset_y, -(self.canvas_surface.get_height() * self.zoom - self.height) / self.zoom), 0)

            # Handle mouse button down for dragging or selecting shapes
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # if event.button == 1:  # Left mouse button
                # if self.in_canvas(event.pos):                
                # Check if a shape is being clicked for selection
                mouse_x, mouse_y = (event.pos[0] - self.x - self.offset_x) / self.zoom, (event.pos[1] - self.y - self.offset_y) / self.zoom
                print(f'cursor location:{mouse_x}, {mouse_y}', end='')
                for shape in self.shapes:
                    self.dragging_vertex = shape.get_closest_vertex((mouse_x, mouse_y))
                    
                    if  self.dragging_vertex is not None:
                        self.resizing_polygon = True
                        self.selected_polygon = shape
                        return
                    if shape.point_in_polygon((mouse_x, mouse_y)):                        
                        self.drag_start = ((event.pos[0] - self.x), (event.pos[1] - self.y))
                        self.moving_polygon = True
                        self.selected_polygon = shape
                        return

                # If no shape is selected, start dragging the canvas
                self.panning = True
                self.drag_start = ((event.pos[0] - self.x), (event.pos[1] - self.y))
                print(f', nothing clicked, drag started at: {self.drag_start[0]}, {self.drag_start[1]}')

            # Handle mouse button up for stopping dragging or resizing
            if event.type == pygame.MOUSEBUTTONUP:            
                if event.button == 1:  # Left mouse button
                    self.panning = False
                    self.moving_polygon = False
                    self.resizing_polygon = False
                    print(f'offset: {self.offset_x - self.drag_start[0]}, {self.offset_y - self.drag_start[1]}')
            
            # Handle mouse motion for dragging or resizing
            if event.type == pygame.MOUSEMOTION:
                if self.panning:
                    # Update canvas offset
                    dx, dy = (event.pos[0] - self.x - self.drag_start[0]), (event.pos[1] - self.y - self.drag_start[1])
                    # dx, dy = event.pos[0] - self.x - self.drag_start[0], event.pos[1] - self.y - self.drag_start[1]
                    self.offset_x += dx / self.zoom
                    self.offset_y += dy / self.zoom
                    self.drag_start = ((event.pos[0] - self.x), (event.pos[1] - self.y))
                    print(f'drag started at: {self.drag_start[0]}, {self.drag_start[1]}, offset: {dx}, {dy}')
                    self.offset_x = min(max(self.offset_x, -(self.canvas_surface.get_width() * self.zoom - self.width) / self.zoom), 0)
                    self.offset_y = min(max(self.offset_y, -(self.canvas_surface.get_height() * self.zoom - self.height) / self.zoom), 0)
                
                elif self.moving_polygon:
                    dx, dy = (event.pos[0] - self.x - self.drag_start[0]) / self.zoom, (event.pos[1] - self.y - self.drag_start[1] / self.zoom)
                    self.drag_start = ((event.pos[0] - self.x), (event.pos[1] - self.y))
                    self.selected_polygon.move_polygon((dx, dy))
                    self.update_canvas()
                    
                elif self.resizing_polygon:
                    mouse_x, mouse_y = (event.pos[0] - self.x - self.offset_x) / self.zoom, (event.pos[1] - self.y - self.offset_y) / self.zoom
                    self.selected_polygon.update_vertex(self.dragging_vertex, (mouse_x, mouse_y))
                    self.update_canvas()
    
    def draw(self):
        # Calculate the viewable area of the canvas
        view_rect = pygame.Rect(
            -self.offset_x / self.zoom,
            -self.offset_y / self.zoom,
            min(self.width / self.zoom, self.canvas_surface.get_width()),
            min(self.height / self.zoom, self.canvas_surface.get_height())
        )

        # Ensure the view_rect is within the bounds of the canvas surface
        view_rect.clamp_ip(pygame.Rect(0, 0, self.canvas_surface.get_width(), self.canvas_surface.get_height()))

        # Clip the canvas to the viewable area
        visible_surface = self.canvas_surface.subsurface(view_rect)

        # Scale the visible surface
        scaled_surface = pygame.transform.smoothscale(visible_surface, (
            int(view_rect.width * self.zoom),
            int(view_rect.height * self.zoom)
        ))

        # Blit the scaled portion of the canvas onto the parent surface
        self.parent_surface.blit(scaled_surface, (self.x, self.y))

    def add_shape(self, shape):
        self.shapes.append(shape)
        self.update_canvas()
    
    def draw_shapes(self):
        for shape in self.shapes:            
            shape.render(self.canvas_surface)

    def update_canvas(self):
        self.initialize_canvas()
        self.draw_shapes()

if __name__ == "__main__":

    def output_polygons(filename):
        with open(filename, 'w') as f:
            for p in canvas.shapes:                
                f.write(f"Polygon Vertices: {p.vertices}\n")
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

    def read_file_as_lists(filename):
        polygons = []
        with open(filename, 'r') as file:
            for line in file:
                # Extract the portion of line that contains the list of vertices
                if "Polygon Vertices:" in line:
                    vertices_str = line.split("Polygon Vertices: ")[1].strip()
                    # Convert the string representation of the list into an actual list
                    vertices = ast.literal_eval(vertices_str)
                    polygon = Polygon(vertices)
                    polygons.append(polygon)
        return polygons


    pygame.init()
    screen = pygame.display.set_mode((1000, 600))
    pygame.display.set_caption("Main Window with Zoomable Canvas and Buttons")
    manager = pygame_gui.UIManager((1000, 600))

    # Create ZoomableCanvas instance
    # init_kspace_canvas = partial(init_kspace_canvas, n1=1.54, n2=2)
    init_kspace = Init_Kspace(1, 2)
    canvas = ZoomableCanvas(screen, 400, 0, 400, 400, 400, 400, scale=100, init_canvas=init_kspace, px_to_coord=px_to_kspace)

    # Create buttons using pygame_gui
    polygon_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (150, 40)), text='Add Polygons', manager=manager)
    output_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 60), (150, 40)), text='Output Polygons', manager=manager)
    dummy_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 110), (150, 40)), text='Dummy', manager=manager)
    


    clock = pygame.time.Clock()

    # Main loop
    while True:
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Handle button clicks
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == output_button:
                        print("Button Circle clicked!")

                        output_polygons('polygon_layout.txt')
                        # canvas.add_shape("circle", color=BLUE, position=(800, 800), radius=50)
                    elif event.ui_element == dummy_button:
                        init_kspace.n2 = 2.6
                        canvas.update_canvas()
                        print("Button Rectangle clicked!")
                        # canvas.add_shape("rectangle", color=RED, rect=pygame.Rect(100, 100, 200, 100))
                    elif event.ui_element == polygon_button:
                        print("Button Polygon clicked!")
                        fov_red = KSpaceFOV(canvas, (0, 0), 30, 30, 0.5, (255, 0, 0, 128))
                        fov_green = KSpaceFOV(canvas, (1.5, 0), 30, 30, 0.15, (0, 255, 0, 128))
                        fov_blue = KSpaceFOV(canvas, (0, -1.5), 30, 30, 0.01, (0, 0, 255, 128))
                        canvas.add_shape(fov_red)
                        canvas.add_shape(fov_green)
                        canvas.add_shape(fov_blue)
                        
                        # polygons = read_file_as_lists('polygon_layout.txt')
                        # for p in polygons:
                        #     canvas.add_shape(p)

            # Pass events to manager and canvas
            manager.process_events(event)
            canvas.handle_event(event)

        # Update manager
        manager.update(time_delta)

        # Draw everything
        screen.fill((200, 200, 200))  # Clear screen with a background color
        canvas.draw()
        manager.draw_ui(screen)
        pygame.display.flip()
