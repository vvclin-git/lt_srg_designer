import pygame
import pygame_gui

pygame.init()

# Set up the screen and manager
screen = pygame.display.set_mode((800, 600))
manager = pygame_gui.UIManager((800, 600))

# Create a UITextEntryLine
text_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((350, 275), (100, 50)), manager=manager)

clock = pygame.time.Clock()
is_running = True

while is_running:
    time_delta = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False

        # Check for UITextEntryLine finishing event
        if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
            if event.ui_element == text_entry:
                # The user pressed enter and finished the text entry
                print(f"User entered: {event.text}")

        # Pass events to the UI manager
        manager.process_events(event)

    manager.update(time_delta)

    # Drawing
    screen.fill((0, 0, 0))
    manager.draw_ui(screen)

    pygame.display.update()

pygame.quit()
