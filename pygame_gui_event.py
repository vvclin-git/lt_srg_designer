import pygame
import pygame_gui
import pygame_gui._constants as constants

def get_pygame_gui_event_name(event):
    # Create a reverse lookup dictionary
    event_type_to_name = {getattr(constants, attr): attr
                          for attr in dir(constants)
                          if not attr.startswith('__') and isinstance(getattr(constants, attr), int)}
    
    # Get the event name
    event_number = event.type
    return event_type_to_name.get(event_number, 'Unknown Event')

pygame.init()

# Set up the display
pygame.display.set_caption('UI Elements Separated by Object ID')
window_surface = pygame.display.set_mode((800, 800))

# Create the UI manager
ui_manager = pygame_gui.UIManager((800, 800))

# Create UI elements for Group A
button_A = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((50, 50), (100, 50)),
    text='Button A',
    manager=ui_manager,
    object_id="A"
)

dropdown_A = pygame_gui.elements.UIDropDownMenu(
    options_list=["Option A1", "Option A2", "Option A3"],
    starting_option="Option A1",
    relative_rect=pygame.Rect((200, 50), (200, 50)),
    manager=ui_manager,
    object_id="A"
)

slider_A = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((50, 150), (300, 50)),
    start_value=50,
    value_range=(0, 100),
    manager=ui_manager,
    object_id="A"
)

text_entry_A1 = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((50, 220), (300, 50)),
    manager=ui_manager,
    object_id="A"
)
text_entry_A1.set_text("Group A Text Entry 1")

text_entry_A2 = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((50, 290), (300, 50)),
    manager=ui_manager,
    object_id="A"
)
text_entry_A2.set_text("Group A Text Entry 2")

# Create UI elements for Group B
button_B = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((50, 400), (100, 50)),
    text='Button B',
    manager=ui_manager,
    object_id="B"
)

dropdown_B = pygame_gui.elements.UIDropDownMenu(
    options_list=["Option B1", "Option B2", "Option B3"],
    starting_option="Option B1",
    relative_rect=pygame.Rect((200, 400), (200, 50)),
    manager=ui_manager,
    object_id="B"
)

slider_B = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((50, 500), (300, 50)),
    start_value=30,
    value_range=(0, 100),
    manager=ui_manager,
    object_id="B"
)

text_entry_B1 = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((50, 570), (300, 50)),
    manager=ui_manager,
    object_id="B"
)
text_entry_B1.set_text("Group B Text Entry 1")

text_entry_B2 = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((50, 640), (300, 50)),
    manager=ui_manager,
    object_id="B"
)
text_entry_B2.set_text("Group B Text Entry 2")

clock = pygame.time.Clock()
is_running = True

while is_running:
    time_delta = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
        
        # Handle all significant pygame_gui events dynamically 
        if event.type in [pygame_gui.UI_BUTTON_PRESSED, pygame_gui.UI_DROP_DOWN_MENU_CHANGED, pygame_gui.UI_HORIZONTAL_SLIDER_MOVED, pygame_gui.UI_TEXT_ENTRY_FINISHED]:
            if 'ui_element' in event.__dict__:
                object_id = event.__dict__['ui_object_id']
                event_name = get_pygame_gui_event_name(event)
                print(f"Event from Object ID: {object_id}")
                print(f"Triggered by element: {event.ui_element}")
                print(f"Event Name: {event_name}")
                print(f"Event Details: {event.__dict__}")
                
                # Handle Group A events
                if object_id.startswith("A"):
                    print("This event belongs to Group A.")

                # Handle Group B events
                elif "B" in object_id:
                    print("This event belongs to Group B.")
        
        # Pass the event to the UI manager
        ui_manager.process_events(event)

    # Update the UI
    ui_manager.update(time_delta)

    # Draw the UI
    window_surface.fill((0, 0, 0))  # Clear the screen
    ui_manager.draw_ui(window_surface)

    pygame.display.update()

pygame.quit()
