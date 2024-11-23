import pygame
import pygame_gui
import json
import re
import numpy as np
from pygame_gui.elements import UIPanel, UILabel, UITextEntryLine, UIButton

class TableWidget:
    def __init__(self, parent_rect, manager, headers, data, label_ratio=0.4, gap_width=10, connected_objs=[], object_id=''):

        theme = manager.ui_theme        
        label_font_size = theme.ui_element_fonts_info['label']['en']['size'] 
        text_entry_font_size = theme.ui_element_fonts_info['text_entry_line']['en']['size']  
        font_size = max((label_font_size, text_entry_font_size))
        self.row_height = round(font_size * 1.4) 
        self.manager = manager
        self.error_dialogue = None
        self.last_valid_input = ''
        self.connected_objs = connected_objs
        # Set up table data
        self.headers = headers
        self.data = data


        # Create a panel to hold the table, panel size depends on parent rect
        panel_width = parent_rect.width
        panel_height = int(self.row_height * (len(self.data) + 1)) + 2 * gap_width
        # self.panel = UIPanel(relative_rect=pygame.Rect((0, 0), (panel_width, panel_height)), manager=self.manager)
        self.panel = UIPanel(relative_rect=pygame.Rect(parent_rect.topleft, (panel_width, panel_height)), manager=self.manager)

        # Calculate label and text entry width based on panel size ratio
        label_width = round((panel_width - gap_width * 3) * label_ratio)        
        editable_width = round((panel_width - gap_width * 3) * (1 - label_ratio))              
        # Create header labels
        self.header_labels = []
        x_offset = gap_width
        for i, header in enumerate(self.headers):
            header_label = UILabel(relative_rect=pygame.Rect((x_offset, gap_width), (label_width, self.row_height)), text=header, manager=self.manager, container=self.panel, anchors={'left': 'left'})
            self.header_labels.append(header_label)
            x_offset += label_width + gap_width

        # Create data labels and editable fields
        self.data_labels = []        
        self.data_value_fields = []
        self.data_values = []
        y_offset = gap_width + self.row_height
        for row in self.data:
            x_offset = gap_width
            
            cell_label = UILabel(relative_rect=pygame.Rect((x_offset, y_offset), (label_width, self.row_height)), text=row['label'], manager=self.manager, container=self.panel, anchors={'left': 'left'})
            self.data_labels.append(cell_label)
            
            if row['static']:
                data_static = UILabel(relative_rect=pygame.Rect((x_offset + label_width + gap_width, y_offset), (editable_width, self.row_height)), text=row['value'], manager=self.manager, container=self.panel, anchors={'left': 'left'})
                self.data_value_fields.append(data_static)                
            else:
                data_entry = UITextEntryLine(relative_rect=pygame.Rect((x_offset + label_width + gap_width, y_offset), (editable_width, self.row_height)), manager=self.manager, container=self.panel, anchors={'left': 'left'}, object_id=object_id)                        
                data_entry.set_text(row['value']) 
                self.data_value_fields.append(data_entry)
            
            self.data_values.append(row['value'])
            y_offset += self.row_height

    def load_data(self, numpy_array):
        if len(numpy_array) != len(self.data_values):
            raise ValueError("Input data length does not match the number of editable fields.")
        for entry, value in zip(self.data_value_fields, numpy_array):
            entry.set_text(str(value))
    
    def test_regex(self, input_string, regex_pattern):        
        return bool(re.fullmatch(regex_pattern, input_string))

    def handle_event(self, event):
        # Event handler that is triggered when events occur
        if event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
            for i, text_entry in enumerate(self.data_value_fields):                
                if event.ui_element == text_entry:
                    regex_str = self.data[i]['regex']
                    self.on_text_input_finish(text_entry, regex_str)
                    break
            self.data_values[i] = text_entry.get_text()            
            for c in self.connected_objs:
                c.update(self.data_values)
        # if event.type == pygame_gui.UI_BUTTON_PRESSED and self.error_dialog is not None:
        #     if event.ui_element.text == "Dismiss":
        #         self.error_dialog.kill()
        #         self.error_dialog = None  # Reset dialog tracking

    def on_text_input_finish(self, text_entry, regex_str):
        input_text = text_entry.get_text()
        if input_text.strip() == "":
                print("Input is empty, waiting for user input...")
        elif self.test_regex(input_text, regex_str):
            # Valid input: Update the last valid input and print
            self.last_valid_input = input_text
            print(f"Valid input: {input_text}")
        else:
            # Invalid input: Revert to the last valid input
            if self.error_dialogue is None:
                self.error_dialogue = pygame_gui.windows.UIMessageWindow(
                    rect=pygame.Rect((250, 200), (300, 150)),
                    html_message=f'Invalid input: "{input_text}". Reverting to last valid input: "{self.last_valid_input}".',
                    manager=self.manager,
                    window_title='Input Error'
                )
            text_entry.set_text(self.last_valid_input)
        print("Text input finished: ", text_entry.get_text())

    def update(self):
        self.load_data(self.data_values)

    def output_data(self):
        # values = [data_value.get_text() for data_value in self.data_values]        
        return np.array(self.data_values)

if __name__ == "__main__":
    # Initialize pygame
    pygame.init()

    # Set up main display
    window_size = (500, 500)
    window = pygame.display.set_mode(window_size)
    pygame.display.set_caption('Table Widget Test')
    # Set up GUI manager
    theme_path = '.\\Widgets\\theme.json'
    gui_manager = pygame_gui.UIManager(window_size, theme_path)
    

    # Set up table data
    headers = ['Parameter', 'Value']
    # data = [
    # {'label': 'Scale', 'value': '0.5', 'static': False},
    # {'label': 'Pixel Number', 'value': '5x5', 'static': True},
    # {'label': 'Pixel Pitch', 'value': '60x60', 'static': True},
    # {'label': 'Pixel Size', 'value': '50x50', 'static': False},
    # {'label': 'Row Offset', 'value': '0', 'static': False},
    # {'label': 'Sub-pixel Pitch', 'value': '30x30', 'static': False},
    # {'label': 'Sub-pixel Size', 'value': '20x20', 'static': False},
    # {'label': 'Sub-pixel Padding', 'value': '0x0', 'static': False},
    # {'label': 'Sub-pixel Order', 'value': 'RG|BW', 'static': False}
    # ]
    with open('sys_params.json') as f:
        data = json.load(f)
    

    # Create table widget
    table_widget = TableWidget(pygame.Rect((15, 30), (470, 300)), headers=headers, data=data, label_ratio=0.5, gap_width=5, manager=gui_manager)
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
                        table_widget.data_values = test_data
                        table_widget.update()
                        # table_widget.load_data(test_data)
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
            table_widget.handle_event(event)
        gui_manager.update(time_delta)

        # Draw background
        window.fill((255, 255, 255))

        # Update GUI manager
        gui_manager.draw_ui(window)

        # Update display
        pygame.display.flip()

    pygame.quit()
