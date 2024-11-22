import pygame
import pygame_gui

class EventInterceptor:
    def __init__(self):
        # Store handlers for UI elements by their `object_id`
        self.ui_handlers = {}
        # Custom event handlers for canvas and shapes
        self.custom_handlers = []

    def add_handler(self, ui_object_id, handler, event_type=None):
        """Associate a UI element (identified by `object_id`) with a handler."""
        if event_type:
            self.ui_handlers.setdefault(event_type, {})[ui_object_id] = handler
        else:
            self.ui_handlers.setdefault(None, {})[ui_object_id] = handler

    def add_custom_handler(self, handler):
        """Add custom handler for non-standard UI elements."""
        self.custom_handlers.append(handler)

    def handle_event(self, event):
        """Intercept and handle events."""
        # Handle pygame_gui events
        if hasattr(event, 'ui_element'):
            ui_element = event.ui_element
            ui_object_id = ui_element.object_ids[0] if ui_element.object_ids else None
            event_handlers = self.ui_handlers.get(event.type, {}) or self.ui_handlers.get(None, {})
            handler = event_handlers.get(ui_object_id)
            if handler:
                handler(event)

        # Handle custom events
        for custom_handler in self.custom_handlers:
            custom_handler(event)

# Initialize pygame and pygame_gui
pygame.init()
screen = pygame.display.set_mode((800, 600))
manager = pygame_gui.UIManager((800, 600))

# Add UI elements
text_input = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((100, 100), (200, 50)),
                                                  manager=manager,
                                                  object_id='#text_input')

button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 200), (100, 50)),
                                       text='Button',
                                       manager=manager,
                                       object_id='#button')

# Custom Canvas (pygame surface)
canvas = pygame.Surface((300, 300))
canvas_rect = canvas.get_rect(topleft=(400, 100))

# Draw shapes on canvas
shapes = [
    pygame.Rect(50, 50, 100, 100),  # Example rectangle
]

# Define handlers
def handle_text_input(event):
    if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
        print(f"Text input submitted: {event.text}")

def handle_button_click(event):
    print("Button clicked!")

def handle_canvas_click(event):
    if event.type == pygame.MOUSEBUTTONDOWN:
        mouse_pos = event.pos
        for shape in shapes:
            shape_global_pos = shape.move(canvas_rect.topleft)
            if shape_global_pos.collidepoint(mouse_pos):
                print(f"Clicked on shape at {shape.topleft}")

# Create and configure EventInterceptor
interceptor = EventInterceptor()
interceptor.add_handler('#text_input', handle_text_input, pygame_gui.UI_TEXT_ENTRY_FINISHED)
interceptor.add_handler('#button', handle_button_click, pygame_gui.UI_BUTTON_PRESSED)
interceptor.add_custom_handler(handle_canvas_click)

# Main loop
clock = pygame.time.Clock()
running = True

while running:
    time_delta = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Pass the event to the EventInterceptor
        interceptor.handle_event(event)
        # Pass the event to pygame_gui for processing
        manager.process_events(event)

    # Update and draw UI
    manager.update(time_delta)
    screen.fill((0, 0, 0))

    # Draw canvas and shapes
    screen.blit(canvas, canvas_rect.topleft)
    for shape in shapes:
        pygame.draw.rect(canvas, (255, 0, 0), shape)

    # Draw UI elements
    manager.draw_ui(screen)

    pygame.display.update()

pygame.quit()
