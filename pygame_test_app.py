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
    
    def update_vertex(self, index, new_position):
        """Update a specific vertex position."""
        self.vertices[index] = new_position

    def get_closest_vertex(self, mouse_pos, threshold=10):
        """Find the closest vertex to the mouse position."""
        for index, vertex in enumerate(self.vertices):
            if np.linalg.norm(np.array(mouse_pos) - np.array(vertex)) < threshold:  # If close enough to the vertex
                return index
        return None

# Game variables
polygon = None
dragging_vertex = None

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

        if event.type == pygame.MOUSEBUTTONUP:
            dragging_vertex = None  # Stop dragging

        if event.type == pygame.MOUSEMOTION and dragging_vertex is not None:
            # Update the vertex position as the mouse moves
            polygon.update_vertex(dragging_vertex, event.pos)

        # Handle GUI button events
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == create_polygon_button:
                    polygon_size = int(polygon_size_input.get_text())
                    polygon = Polygon(sides=5, size=polygon_size)  # Create a new polygon
                
                if event.ui_element == save_button:
                    # Save polygon vertices to a text file
                    with open('polygon_layout.txt', 'w') as f:
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
