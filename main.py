import ctypes
import pygame
import pygame_gui
from Widgets import ZoomableCanvas, Polygon, CANVAS_MODIFIED_EVENT
from Widgets import TableWidget, KSpaceFOV
import json
import numpy as np
import sys
from lt_srg_designer import *
# Set DPI awareness to bypass Windows scaling
ctypes.windll.user32.SetProcessDPIAware()


# Initialize pygame
pygame.init()


theme_path = '.\\Widgets\\theme.json'
with open('sys_params.json', 'r') as f:
    sys_params = json.load(f)

grating_types = ['ic', 'epe', 'oc']
grating_params_ic = []
grating_params_epe = []
grating_params_oc = []
grating_params = [grating_params_ic, grating_params_epe, grating_params_oc]

for i, t in enumerate(grating_types):
    with open(f'grating_params_{t}.json', 'r') as f:
        grating_params[i] = json.load(f)

# Set up the display
window_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('DOE Layout Designer')

# Set up the UI manager
manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT), theme_path=theme_path)

lt_srg_designer = LT_SRG_Designer(window_surface, manager, sys_params, grating_params)

# Run the game loop
clock = pygame.time.Clock()

is_running = True
while is_running:
    time_delta = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            is_running = False
            

        manager.process_events(event)
        lt_srg_designer.handle_event(event)
       
    manager.update(time_delta)
    window_surface.fill((255, 255, 255))
    manager.draw_ui(window_surface)
    lt_srg_designer.draw()
 
    pygame.display.update()

pygame.quit()
