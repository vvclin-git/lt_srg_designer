import pygame
import pygame_gui

pygame.init()

# Set up the display
pygame.display.set_caption('UI Elements Separated by Object ID')
window_surface = pygame.display.set_mode((800, 600))

# Create the UI manager
ui_manager = pygame_gui.UIManager((800, 600))

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

# Create UI elements for Group B
button_B = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((50, 250), (100, 50)),
    text='Button B',
    manager=ui_manager,
    object_id="B"
)

dropdown_B = pygame_gui.elements.UIDropDownMenu(
    options_list=["Option B1", "Option B2", "Option B3"],
    starting_option="Option B1",
    relative_rect=pygame.Rect((200, 250), (200, 50)),
    manager=ui_manager,
    object_id="B"
)

slider_B = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((50, 350), (300, 50)),
    start_value=30,
    value_range=(0, 100),
    manager=ui_manager,
    object_id="B"
)

clock = pygame.time.Clock()
is_running = True

while is_running:
    time_delta = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
        
        # Handle all pygame.USEREVENTs dynamically
        # if event.type == pygame.USEREVENT:
        # if event.type == pygame.USEREVENT and not event.type == pygame_gui.UI_BUTTON_ON_HOVERED:
        if event.type == pygame.USEREVENT and event.__dict__.get('user_type') not in [32870, 32871]:
            if 'ui_element' in event.__dict__:
                object_id = event.__dict__['ui_object_id']  # Corrected to access the attribute directly
                print(f"Event from Object ID: {object_id}")
                print(f"Triggered by element: {event.ui_element}")
                print(f"Event Details: {event.__dict__}")
                
                # Handle Group A events
                if "A" in object_id:
                    print("This event belongs to Group A.")
                
                # Handle Group B events
                elif "B" in object_id:
                    print("This event belongs to Group B.")u7u
        
        # Pass the event to the UI manager
        ui_manager.process_events(event)

    # Update the UI
    ui_manager.update(time_delta)

    # Draw the UI
    window_surface.fill((0, 0, 0))  # Clear the screen
    ui_manager.draw_ui(window_surface)

    pygame.display.update()

pygame.quit()
