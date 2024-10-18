import pygame
import pygame_gui

# Initialize Pygame and Pygame GUI
pygame.init()

# Set up the Pygame window
window_size = (400, 300)
window = pygame.display.set_mode(window_size)
pygame.display.set_caption('Pygame GUI Button Example')

# Set up the UI Manager
manager = pygame_gui.UIManager(window_size)

# Create a button
button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((150, 120), (100, 50)),
                                      text='Click Me!',
                                      manager=manager)

# Clock to control the frame rate
clock = pygame.time.Clock()

running = True
while running:
    time_delta = clock.tick(60) / 1000.0  # Control frame rate to 60 FPS
    
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Handle button click event
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == button:
                print('Button was clicked!')
                
        # Pass the event to the UI Manager
        manager.process_events(event)

    # Update the UI Manager
    manager.update(time_delta)

    # Draw the UI
    window.fill((0, 0, 0))  # Fill the screen with black
    manager.draw_ui(window)

    # Update the display
    pygame.display.update()

# Quit Pygame
pygame.quit()
