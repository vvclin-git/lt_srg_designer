import pygame
import pygame_gui
import sys
import numpy as np

WHITE = (255, 255, 255)
BLACK = (0, 0, 0) 
BLUE = (0, 0, 255, 50)
RED = (255, 0, 0, 50)
GREY_D = (100, 100, 100)
GREY_L = (200, 200, 200)


class ZoomableCanvas:
    def __init__(self, parent_surface, x, y, width, height, canvas_width, canvas_height, grid=True, grid_size=100, bg_color=WHITE, shapes=[]):
        self.parent_surface = parent_surface
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.shapes = shapes
        self.bg_color = bg_color
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.grid = grid
        self.grid_size = grid_size        
        # Create a canvas surface
        self.canvas_surface = pygame.Surface((canvas_width, canvas_height))
        self.initialize_canvas()       

        # Zoom and pan variables
        self.zoom = 1.0
        self.offset_x, self.offset_y = 0, 0
        self.dragging = False
        self.drag_start = (0, 0)
        self.selected_shape = None
        self.resizing_shape = False
        self.resize_margin = 10
    
    def initialize_canvas(self):
        # Initialize canvas with background color, grid, and border
        self.canvas_surface.fill(self.bg_color)
        pygame.draw.rect(self.canvas_surface, BLACK, pygame.Rect(0, 0, self.canvas_width, self.canvas_height), 2)
        if self.grid:
            canvas_dimension = np.array([self.canvas_width, self.canvas_height])
            grid_line_num = np.array([int(self.canvas_width / self.grid_size) + 1, int(self.canvas_height / self.grid_size) + 1])
            grid_line_start_pos = ((canvas_dimension - (grid_line_num - 1) * self.grid_size) * 0.5).astype(int)
            for i in range(grid_line_num[0]):
                pygame.draw.line(self.canvas_surface, BLACK, (grid_line_start_pos[0] + i * self.grid_size, 0), (grid_line_start_pos[0] + i * self.grid_size, canvas_dimension[1]), width=2)
            for j in range(grid_line_num[1]):
                pygame.draw.line(self.canvas_surface, BLACK, (0, grid_line_start_pos[1] + j * self.grid_size), (canvas_dimension[0], grid_line_start_pos[1] + j * self.grid_size), width=2)
            
    
    def in_canvas(self, pos):
        if self.x <= pos[0] <= self.x + self.width and self.y <= pos[1] <= self.y + self.height:
            return True
        return False


    def handle_event(self, event):
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
            self.zoom = max(0.1, min(self.zoom, 5.0))

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
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                if self.in_canvas(event.pos):                
                    # Check if a shape is being clicked for selection
                    mouse_x, mouse_y = (event.pos[0] - self.x - self.offset_x) / self.zoom, (event.pos[1] - self.y - self.offset_y) / self.zoom
                    print(f'cursor location:{mouse_x}, {mouse_y}', end='')
                    for shape in self.shapes:
                        if shape[0] == 'rectangle':
                            rect = shape[1]['rect']
                            if rect.collidepoint(mouse_x, mouse_y):
                                self.selected_shape = shape
                                print(f', rectangle clicked at rect:{rect.x}, {rect.y}')
                                self.dragging = True
                                # if abs(mouse_x - rect.right) < self.resize_margin or abs(mouse_y - rect.bottom) < self.resize_margin:
                                #     self.resizing_shape = True
                                # else:
                                #     self.dragging = True
                                self.drag_start = ((event.pos[0] - self.x), (event.pos[1] - self.y))
                                return
                    # If no shape is selected, start dragging the canvas
                    self.dragging = True
                    self.drag_start = ((event.pos[0] - self.x), (event.pos[1] - self.y))
                    print(f', nothing clicked, drag started at: {self.drag_start[0]}, {self.drag_start[1]}')

        # Handle mouse button up for stopping dragging or resizing
        if event.type == pygame.MOUSEBUTTONUP:            
            if event.button == 1:  # Left mouse button
                self.dragging = False
                self.resizing_shape = False
                self.selected_shape = None
                print(f'offset: {self.offset_x - self.drag_start[0]}, {self.offset_y - self.drag_start[1]}')
        # Handle mouse motion for dragging or resizing
        if event.type == pygame.MOUSEMOTION:
            if self.dragging and not self.resizing_shape:
                if self.selected_shape is not None:
                    # Update shape position
                    dx, dy = (event.pos[0] - self.x - self.drag_start[0]), (event.pos[1] - self.y - self.drag_start[1])
                    rect = self.selected_shape[1]['rect']
                    rect.x += dx / self.zoom
                    rect.y += dy / self.zoom
                    self.drag_start = ((event.pos[0] - self.x), (event.pos[1] - self.y))
                    print(f'drag started at: {self.drag_start[0]}, {self.drag_start[1]}, offset: {dx}, {dy}')
                    self.update_canvas()
                else:
                    # Update canvas offset
                    dx, dy = (event.pos[0] - self.x - self.drag_start[0]), (event.pos[1] - self.y - self.drag_start[1])
                    # dx, dy = event.pos[0] - self.x - self.drag_start[0], event.pos[1] - self.y - self.drag_start[1]
                    self.offset_x += dx / self.zoom
                    self.offset_y += dy / self.zoom
                    self.drag_start = ((event.pos[0] - self.x), (event.pos[1] - self.y))
                    print(f'drag started at: {self.drag_start[0]}, {self.drag_start[1]}, offset: {dx}, {dy}')

                # Ensure offset stays within bounds while dragging
                self.offset_x = min(max(self.offset_x, -(self.canvas_surface.get_width() * self.zoom - self.width) / self.zoom), 0)
                self.offset_y = min(max(self.offset_y, -(self.canvas_surface.get_height() * self.zoom - self.height) / self.zoom), 0)

            # if self.resizing_shape and self.selected_shape is not None:
            #     shape_type, params = self.selected_shape
            #     if shape_type == 'rectangle':
            #         rect = params['rect']
            #         rect.width = (event.pos[0] - self.x - self.offset_x) / self.zoom - rect.x
            #         rect.height = (event.pos[1] - self.y - self.offset_y) / self.zoom - rect.y



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
        scaled_surface = pygame.transform.scale(visible_surface, (
            int(view_rect.width * self.zoom),
            int(view_rect.height * self.zoom)
        ))

        # Blit the scaled portion of the canvas onto the parent surface
        self.parent_surface.blit(scaled_surface, (self.x, self.y))
    
    def add_shape(self, shape_type, **params):
        if shape_type == "circle":
            self.shapes.append(("circle", params))
        elif shape_type == "rectangle":
            self.shapes.append(("rectangle", params))
        elif shape_type == "polygon":
            self.shapes.append(("polygon", params))
        self.update_canvas()
    
    def draw_shapes(self):
        for shape in self.shapes:
            shape_type, params = shape
            if shape_type == "circle":
                pygame.draw.circle(self.canvas_surface, params["color"], (int(params["position"][0]), int(params["position"][1])), int(params["radius"]))
            elif shape_type == "rectangle":
                rect = params["rect"].copy()
                rect.x = int(rect.x)
                rect.y = int(rect.y)
                rect.width = int(rect.width)
                rect.height = int(rect.height)
                pygame.draw.rect(self.canvas_surface, params["color"], rect)
            elif shape_type == "polygon":
                scaled_points = [(int(x), int(y)) for x, y in params["points"]]
                pygame.draw.polygon(self.canvas_surface, params["color"], scaled_points)

    def update_canvas(self):
        self.initialize_canvas()
        self.draw_shapes()

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1000, 600))
    pygame.display.set_caption("Main Window with Zoomable Canvas and Buttons")
    manager = pygame_gui.UIManager((1000, 600))

    # Create ZoomableCanvas instance
    canvas = ZoomableCanvas(screen, 200, 0, 800, 600, 1600, 1200)

    # Create buttons using pygame_gui
    circle_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (150, 40)), text='Circle', manager=manager)
    rectangle_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 60), (150, 40)), text='Rectangle', manager=manager)
    polygon_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 110), (150, 40)), text='Polygon', manager=manager)
    
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
                    if event.ui_element == circle_button:
                        print("Button Circle clicked!")
                        canvas.add_shape("circle", color=BLUE, position=(800, 800), radius=50)
                    elif event.ui_element == rectangle_button:
                        print("Button Rectangle clicked!")
                        canvas.add_shape("rectangle", color=RED, rect=pygame.Rect(100, 100, 200, 100))
                    elif event.ui_element == polygon_button:
                        print("Button Polygon clicked!")
                        canvas.add_shape("polygon", color=GREY_D, points=[(350, 250), (450, 300), (400, 400)])

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
