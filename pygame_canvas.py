import pygame
import pygame_gui
import sys

class ZoomableCanvas:
    def __init__(self, parent_surface, x, y, width, height, canvas_width, canvas_height):
        self.parent_surface = parent_surface
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        # Create a canvas surface
        self.canvas_surface = pygame.Surface((canvas_width, canvas_height))
        self.canvas_surface.fill((255, 255, 255))  # Fill with white
        pygame.draw.circle(self.canvas_surface, (255, 0, 0), (canvas_width // 2, canvas_height // 2), 100)  # Example drawing

        # Zoom and pan variables
        self.zoom = 1.0
        self.offset_x, self.offset_y = 0, 0
        self.dragging = False
        self.drag_start = (0, 0)

    def handle_event(self, event):
        if event.type == pygame.MOUSEWHEEL:
            old_zoom = self.zoom
            if event.y > 0:  # Zoom in
                self.zoom *= 1.1
            elif event.y < 0:  # Zoom out
                self.zoom /= 1.1

            # Limit zoom to reasonable levels
            self.zoom = max(0.1, min(self.zoom, 5.0))

            # Adjust offset to keep the zoom centered around the mouse position
            if hasattr(event, 'pos'):
                mouse_x, mouse_y = event.pos
                rel_x = (mouse_x - self.x - self.offset_x) / old_zoom
                rel_y = (mouse_y - self.y - self.offset_y) / old_zoom
                self.offset_x = mouse_x - self.x - rel_x * self.zoom
                self.offset_y = mouse_y - self.y - rel_y * self.zoom

            # Ensure offset stays within bounds after zooming
            self.offset_x = min(max(self.offset_x, -(self.canvas_surface.get_width() * self.zoom - self.width) / self.zoom), 0)
            self.offset_y = min(max(self.offset_y, -(self.canvas_surface.get_height() * self.zoom - self.height) / self.zoom), 0)

        # Handle mouse button down for dragging
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                if self.x <= event.pos[0] <= self.x + self.width and self.y <= event.pos[1] <= self.y + self.height:
                    self.dragging = True
                    self.drag_start = (event.pos[0] - self.x, event.pos[1] - self.y)

        # Handle mouse button up for stopping dragging
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button
                self.dragging = False

        # Handle mouse motion for dragging
        if event.type == pygame.MOUSEMOTION:
            if self.dragging:
                dx, dy = event.pos[0] - self.x - self.drag_start[0], event.pos[1] - self.y - self.drag_start[1]
                self.offset_x += dx
                self.offset_y += dy
                self.drag_start = (event.pos[0] - self.x, event.pos[1] - self.y)

                # Ensure offset stays within bounds while dragging
                self.offset_x = min(max(self.offset_x, -(self.canvas_surface.get_width() * self.zoom - self.width) / self.zoom), 0)
                self.offset_y = min(max(self.offset_y, -(self.canvas_surface.get_height() * self.zoom - self.height) / self.zoom), 0)

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
                    elif event.ui_element == rectangle_button:
                        print("Button Rectangle clicked!")
                    elif event.ui_element == polygon_button:
                        print("Button Polygon clicked!")

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
