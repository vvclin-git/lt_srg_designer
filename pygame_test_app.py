import pygame
import pygame_gui
import numpy as np

pygame.init()

# Set up screen
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

# Set up pygame_gui manager
manager = pygame_gui.UIManager((screen_width, screen_height))

# Create UI elements
polygon_size_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((10, 10), (100, 30)),
                                                 text="Polygon Size:",
                                                 manager=manager)
polygon_size_input = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((120, 10), (100, 30)),
                                                         manager=manager)

create_polygon_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 50), (100, 30)),
                                                     text="Create Polygon",
                                                     manager=manager)

save_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((120, 50), (100, 30)),
                                           text="Save Layout",
                                           manager=manager)

# Polygon class
class Polygon:
    def __init__(self, sides, size, center=(400, 300)):
        self.sides = sides
        self.size = size
        self.center = center
        self.vertices = self.create_polygon()
    
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
                pygame.draw.circle(screen, (255, 0, 0), (int(vertex[0]), int(vertex[1])), 5)  # Draw vertices as red dots
    
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
            print(self.vertices[i][0], distance)

            self.vertices[i] = (self.vertices[i][0] + distance[0], self.vertices[i][1] + distance[1])

    def get_closest_vertex(self, mouse_pos, threshold=10):
        """Find the closest vertex to the mouse position."""
        for index, vertex in enumerate(self.vertices):
            if np.linalg.norm(np.array(mouse_pos) - np.array(vertex)) < threshold:  # If close enough to the vertex
                return index
        return None

# Game variables
polygon = None
dragging_vertex = None
dragging_polygon = False
drag_start = (0, 0)
clock = pygame.time.Clock()
running = True

while running:
    time_delta = clock.tick(60) / 1000.0
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Handle pygame_gui events
        manager.process_events(event)
        
        # Handle mouse events for polygon manipulation
        if event.type == pygame.MOUSEBUTTONDOWN:
            if polygon:
                closest_vertex = polygon.get_closest_vertex(event.pos)
                if closest_vertex is not None:
                    dragging_vertex = closest_vertex  # Start dragging the vertex
                else:
                    if polygon.point_in_polygon(event.pos):
                        print('move polygon True', end='')
                        dragging_polygon = True
                        drag_start = event.pos
                        print(f', starting point:{event.pos}')
                    else:
                        print('move polygon False')
                        


        if event.type == pygame.MOUSEBUTTONUP:
            dragging_vertex = None  # Stop dragging
            dragging_polygon = False

        if event.type == pygame.MOUSEMOTION and polygon is not None and dragging_vertex is not None:
            # Update the vertex position as the mouse moves
            polygon.update_vertex(dragging_vertex, event.pos)
        
        if event.type == pygame.MOUSEMOTION and polygon is not None and dragging_polygon is not False:
            # Update the vertex position as the mouse moves
            print(f'drag start pos: {drag_start}, event pos: {event.pos}')
            drag_distance = (event.pos[0] - drag_start[0], event.pos[1] - drag_start[1])
            polygon.move_polygon(drag_distance)
            drag_start = event.pos

        # Handle GUI button events
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == create_polygon_button:
                    polygon_size = int(polygon_size_input.get_text())
                    polygon = Polygon(sides=5, size=polygon_size)  # Create a new polygon
                
                if event.ui_element == save_button:
                    # Save polygon vertices to a text file
                    with open('polygon_layout.txt', 'a') as f:
                        f.write(f"Polygon Vertices: {polygon.vertices}\n")
    
    # Update pygame_gui manager
    manager.update(time_delta)
    
    # Clear the screen
    screen.fill((255, 255, 255))
    
    # Draw polygon if available
    if polygon:
        polygon.render(screen)
    
    # Render UI
    manager.draw_ui(screen)
    
    # Update the display
    pygame.display.update()

pygame.quit()
