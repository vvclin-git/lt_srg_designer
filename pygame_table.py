import pygame
import pygame_gui
import json
import numpy as np
from pygame_gui.elements import UIPanel, UILabel, UITextEntryLine, UIButton

class TableWidget:
    def __init__(self, parent_rect, headers, data, theme_path, label_ratio=0.4, gap_width=10, static=False, manager=None):
        # Load theme JSON and extract font size
        with open(theme_path, 'r') as theme_file:
            theme_data = json.load(theme_file)
            font_sizes = []
            if 'label' in theme_data and 'font' in theme_data['label'] and 'size' in theme_data['label']['font']:
                font_sizes.append(int(theme_data['label']['font']['size']))
            if 'text_entry' in theme_data and 'font' in theme_data['text_entry'] and 'size' in theme_data['text_entry']['font']:
                font_sizes.append(int(theme_data['text_entry']['font']['size']))
            
            font_size = max(font_sizes) if font_sizes else 12
            self.row_height = round(font_size * 1.4)
            # Extract adjustable parameters from theme
            self.margin = theme_data['layout'].get('margin')
            self.panel_padding = theme_data['layout'].get('panel_padding')

        # Set up GUI manager with theme if not provided
        if manager is None:
            self.manager = pygame_gui.UIManager(parent_rect.size, theme_path)
        else:
            self.manager = manager

        # Set up table data
        self.headers = headers
        self.data = data

        # Create a panel to hold the table, panel size depends on parent rect
        panel_width = parent_rect.width
        panel_height = parent_rect.height        
        # self.panel = UIPanel(relative_rect=pygame.Rect((0, 0), (panel_width, panel_height)), manager=self.manager)
        self.panel = UIPanel(relative_rect=parent_rect, manager=self.manager)

        # Calculate label and text entry width based on panel size ratio
        label_width = round((panel_width - gap_width) * label_ratio)        
        editable_width = panel_width - label_width - gap_width              
        # Create header labels
        self.header_labels = []
        x_offset = 2
        for i, header in enumerate(self.headers):
            header_label = UILabel(relative_rect=pygame.Rect((x_offset, 2), (label_width, self.row_height)), text=header, manager=self.manager, container=self.panel, anchors={'left': 'left'})
            self.header_labels.append(header_label)
            x_offset += label_width + gap_width

        # Create data labels and editable fields
        self.data_labels = []
        self.data_values = []
        y_offset = 2 + self.row_height
        for row_index, row in enumerate(self.data):
            x_offset = 2
            for col_index, cell in enumerate(row):
                if col_index == 1:  # Make the second column editable
                    if not static:
                        cell_value = UITextEntryLine(relative_rect=pygame.Rect((x_offset, y_offset), (editable_width, self.row_height)), manager=self.manager, container=self.panel, anchors={'left': 'left'})
                    else:
                        cell_value = UILabel(relative_rect=pygame.Rect((x_offset, y_offset), (editable_width, self.row_height)), text=cell, manager=self.manager, container=self.panel, anchors={'left': 'left'})
                    cell_value.set_text(cell)                    
                    self.data_labels.append(cell_value)
                    self.data_values.append(cell_value)
                else:
                    # Make the frame of the 1st column visible and align text to the left
                    cell_label = UILabel(relative_rect=pygame.Rect((x_offset, y_offset), (label_width, self.row_height)), text=cell, manager=self.manager, container=self.panel, anchors={'left': 'left'})
                    self.data_labels.append(cell_label)
                x_offset += label_width + gap_width
            y_offset += self.row_height

    def load_data(self, numpy_array):
        if len(numpy_array) != len(self.data_values):
            raise ValueError("Input data length does not match the number of editable fields.")
        for entry, value in zip(self.data_values, numpy_array):
            entry.set_text(str(value))

    def output_data(self):
        values = [entry.get_text() for entry in self.data_values]
        return np.array(values)

if __name__ == "__main__":
    # Initialize pygame
    pygame.init()

    # Set up main display
    window_size = (500, 500)
    window = pygame.display.set_mode(window_size)
    pygame.display.set_caption('Table Widget Test')
    # Set up GUI manager
    theme_path = 'theme.json'
    gui_manager = pygame_gui.UIManager(window_size, theme_path)
    

    # Set up table data
    headers = ['Parameter', 'Value']
    data = [
        ['Scale', '0.5'],
        ['Pixel Number', '5x5'],
        ['Pixel Pitch', '60x60'],
        ['Pixel Size', '50x50'],
        ['Row Offset', '0'],
        ['Sub-pixel Pitch', '30x30'],
        ['Sub-pixel Size', '20x20'],
        ['Sub-pixel Padding', '0x0'],
        ['Sub-pixel Order', 'RG|BW']
    ]

    # Create table widget
    table_widget = TableWidget(pygame.Rect((15, 30), (470, 300)), headers=headers, data=data, theme_path=theme_path, label_ratio=0.5, gap_width=5, static=False, manager=gui_manager)
    # table_widget = TableWidget(window.get_rect(), headers=headers, data=data, theme_path=theme_path, label_ratio=0.4, editable_ratio=0.4, gap_ratio=0.1, manager=gui_manager)

    # Create buttons for testing data loading and output
    load_button = UIButton(relative_rect=pygame.Rect((40, 440), (100, 40)), text='Load Data', manager=gui_manager)
    output_button = UIButton(relative_rect=pygame.Rect((160, 440), (100, 40)), text='Output Data', manager=gui_manager)

    # Main loop
    clock = pygame.time.Clock()
    running = True
    while running:
        time_delta = clock.tick(30) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False


            # if event.type == pygame.USEREVENT:
            if event.type == pygame_gui.UI_BUTTON_PRESSED:                
                if event.ui_element == load_button:
                    try:
                        test_data = np.array(['1.0', '5x5', '60x60', '50x50', '0', '30x30', '20x20', '0x0', 'RG|BW'])
                        table_widget.load_data(test_data)
                    except ValueError as e:
                        print(e)
                elif event.ui_element == output_button:
                    output = table_widget.output_data()
                    print("Output Data:", output)
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                for label in table_widget.data_labels:
                    if isinstance(label, UILabel) and label.relative_rect.collidepoint(mouse_pos):
                        print("Clicked on UILabel")
                    elif isinstance(label, UITextEntryLine) and label.relative_rect.collidepoint(mouse_pos):
                        print("Clicked on UITextEntryLine")
                if load_button.relative_rect.collidepoint(mouse_pos):
                    print("Clicked on Load Button")
                elif output_button.relative_rect.collidepoint(mouse_pos):
                    print("Clicked on Output Button")
            gui_manager.process_events(event)  # Moved outside of the if block to ensure proper event handling

        gui_manager.update(time_delta)

        # Draw background
        window.fill((255, 255, 255))

        # Update GUI manager
        gui_manager.draw_ui(window)

        # Update display
        pygame.display.flip()

    pygame.quit()
