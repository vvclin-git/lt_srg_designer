import pygame
import pygame_gui
import pygame_gui.elements
import random

class TableGrid:
    def __init__(self, data_dict, panel_rect, manager, panel):
        self.data_dict = data_dict
        self.rows = len(data_dict) + 1  # Including header row
        self.cols = 2  # Parameter name and value
        self.panel_rect = panel_rect
        self.manager = manager
        self.panel = panel
        self.table_grid = []
        self.column_widths = [panel_rect.width // self.cols for _ in range(self.cols)]
        self.create_grid()

    def create_grid(self):
        table_width = self.panel_rect.width - 20
        table_height = self.panel_rect.height - 20
        cell_height = table_height // self.rows

        for row in range(self.rows):
            self.table_grid.append([])
            x_offset = 10
            for col in range(self.cols):
                cell_width = self.column_widths[col]
                if row == 0:
                    # Header row
                    if col == 0:
                        cell_text = 'Parameter Name'
                    else:
                        cell_text = 'Value'
                    background_color = (200, 200, 200)  # Light grey for header row
                else:
                    # Data rows
                    param_name = list(self.data_dict.keys())[row - 1]
                    if col == 0:
                        cell_text = param_name
                    else:
                        cell_text = str(self.data_dict[param_name])
                    background_color = (255, 255, 255)  # White for data rows

                cell = pygame_gui.elements.UITextBox(html_text=cell_text,
                                                     relative_rect=pygame.Rect(x_offset, 10 + row * cell_height, cell_width, cell_height),
                                                     manager=self.manager,
                                                     container=self.panel,
                                                     object_id=f'@table_cell_{row}_{col}')
                # Set background color by modifying the HTML style
                cell.html_text = f'<div style="background-color: rgb{background_color};">{cell_text}</div>'
                cell.rebuild()
                self.table_grid[row].append(cell)
                x_offset += cell_width

    def update_grid_layout(self):
        cell_height = (self.panel_rect.height - 20) // self.rows

        for row in range(self.rows):
            x_offset = 10
            for col in range(self.cols):
                cell_width = self.column_widths[col]
                self.table_grid[row][col].set_relative_rect(pygame.Rect(x_offset, 10 + row * cell_height, cell_width, cell_height))
                x_offset += cell_width
                self.table_grid[row][col].rebuild()

    def get_table_values(self):
        values = {}
        for row in range(1, self.rows):
            param_name = list(self.data_dict.keys())[row - 1]
            param_value = self.data_dict[param_name]
            values[param_name] = param_value
        return values

pygame.init()

# Window Dimensions
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
window_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Custom Layout GUI")

# Colors
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Create the GUI Manager
manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT))

# Define Rects for Layout
layout_canvas_rect = pygame.Rect(10, 10, 500, 580)  # Left side - Layout Canvas
layout_canvas_2_rect = pygame.Rect(520, 10, 270, 250)  # Top-right - Layout Canvas 2
tabulated_data_rect = pygame.Rect(520, 270, 270, 320)  # Bottom-right - Tabulated Data

# Panels with pygame_gui
layout_canvas_2_panel = pygame_gui.elements.UIPanel(relative_rect=layout_canvas_2_rect,
                                                    manager=manager)
tabulated_data_panel = pygame_gui.elements.UIPanel(relative_rect=tabulated_data_rect,
                                                   manager=manager)

# Create TableGrid instance with sample data
data = {
    'Parameter A': 10,
    'Parameter B': 20,
    'Parameter C': 30,
    'Parameter D': 40
}
table_grid = TableGrid(data_dict=data, panel_rect=tabulated_data_rect, manager=manager, panel=tabulated_data_panel)

clock = pygame.time.Clock()
is_running = True

drawing = False
shapes = []

# Main Loop
while is_running:
    time_delta = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False

        # Handle mouse events for interactive drawing in layout_canvas
        if event.type == pygame.MOUSEBUTTONDOWN:
            if layout_canvas_rect.collidepoint(event.pos):
                drawing = True
                start_pos = event.pos
        elif event.type == pygame.MOUSEBUTTONUP:
            if drawing:
                drawing = False
                end_pos = event.pos
                if layout_canvas_rect.collidepoint(end_pos):
                    shape_color = random.choice([BLUE, GREEN, RED])
                    shapes.append((start_pos, end_pos, shape_color))

        manager.process_events(event)

    # Clear the screen
    window_surface.fill(WHITE)

    # Draw Rectangles (Canvas areas)
    pygame.draw.rect(window_surface, RED, layout_canvas_rect, 2)  # Draw Layout Canvas Border

    # Draw shapes in the Layout Canvas
    for shape in shapes:
        pygame.draw.line(window_surface, shape[2], shape[0], shape[1], 3)

    # Update UI Manager
    manager.update(time_delta)

    # Draw GUI elements
    manager.draw_ui(window_surface)

    pygame.display.update()

pygame.quit()