import pygame
import pygame_gui
import re

# Initialize pygame and the GUI manager
pygame.init()

# Screen setup
window_size = (800, 600)
window_surface = pygame.display.set_mode(window_size)
pygame.display.set_caption('Regex Validation Example')
manager = pygame_gui.UIManager(window_size)

# Create a UITextEntryLine
text_entry = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((300, 275), (200, 50)),
    manager=manager
)

# Regex for signed single floating-point number
regex_pattern = r"^[+-]?[1-9]\d*(\.\d+)?$"

# Store the last valid input
last_valid_input = ""

# Clock for managing frame rate
clock = pygame.time.Clock()

# Running loop
running = True
while running:
    time_delta = clock.tick(60) / 1000.0
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Listen for TextChanged event
        if event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED and event.ui_element == text_entry:
            user_input = text_entry.get_text()
            if user_input.strip() == "":
                # Allow empty input but don't update the last valid input
                print("Input is empty, waiting for user input...")
            elif re.fullmatch(regex_pattern, user_input):
                # Valid input: Update the last valid input and print
                last_valid_input = user_input
                print(f"Valid input: {user_input}")
            else:
                # Invalid input: Revert to the last valid input
                pygame_gui.windows.UIMessageWindow(
                    rect=pygame.Rect((250, 200), (300, 150)),
                    html_message=f'Invalid input: "{user_input}". Reverting to last valid input: "{last_valid_input}".',
                    manager=manager,
                    window_title='Input Error'
                )
                text_entry.set_text(last_valid_input)

        # Pass events to the manager
        manager.process_events(event)

    # Update the manager
    manager.update(time_delta)

    # Draw the screen
    window_surface.fill((0, 0, 0))  # Black background
    manager.draw_ui(window_surface)

    pygame.display.update()

# Quit pygame
pygame.quit()
