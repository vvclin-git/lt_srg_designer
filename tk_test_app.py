import tkinter as tk
from tkinter import ttk, Canvas, filedialog
import numpy as np

class SRGApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SRG Layout Designer")

        # Set up layout
        self.create_input_area()
        self.create_canvas_area()

    def create_input_area(self):
        """Create the spreadsheet-like area for inputting parameters"""
        frame = ttk.Frame(self.root)
        frame.grid(row=0, column=0, padx=10, pady=10)

        # Create labels and entries for parameters (e.g., polygon sides, size)
        self.num_sides_label = ttk.Label(frame, text="Number of Sides:")
        self.num_sides_label.grid(row=0, column=0, padx=5, pady=5)
        self.num_sides_entry = ttk.Entry(frame)
        self.num_sides_entry.grid(row=0, column=1, padx=5, pady=5)

        self.size_label = ttk.Label(frame, text="Polygon Size:")
        self.size_label.grid(row=1, column=0, padx=5, pady=5)
        self.size_entry = ttk.Entry(frame)
        self.size_entry.grid(row=1, column=1, padx=5, pady=5)

        self.create_polygon_button = ttk.Button(frame, text="Create Polygon", command=self.create_polygon)
        self.create_polygon_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.save_button = ttk.Button(frame, text="Save Layout", command=self.save_layout)
        self.save_button.grid(row=3, column=0, columnspan=2, pady=10)

    def create_canvas_area(self):
        """Create two canvas areas for displaying and modifying polygons"""
        self.canvas_frame = ttk.Frame(self.root)
        self.canvas_frame.grid(row=0, column=1, padx=10, pady=10)

        # Canvas 1: Display the initial polygon
        self.canvas1 = Canvas(self.canvas_frame, width=300, height=300, bg="white")
        self.canvas1.grid(row=0, column=0, padx=5, pady=5)

        # Canvas 2: Display the editable polygon
        self.canvas2 = Canvas(self.canvas_frame, width=300, height=300, bg="lightgrey")
        self.canvas2.grid(row=0, column=1, padx=5, pady=5)

        self.canvas2.bind("<Button-1>", self.on_click)
        self.canvas2.bind("<B1-Motion>", self.on_drag)

        self.polygon = None  # To store the polygon's data

    def create_polygon(self):
        """Draw a polygon on Canvas 1 based on user input"""
        num_sides = int(self.num_sides_entry.get())
        size = int(self.size_entry.get())
        angle_step = 2 * np.pi / num_sides

        # Calculate polygon vertices
        self.vertices = [(150 + size * np.cos(i * angle_step), 150 + size * np.sin(i * angle_step)) for i in range(num_sides)]

        # Draw polygon in Canvas 1
        self.canvas1.delete("all")
        self.polygon1 = self.canvas1.create_polygon(self.vertices, fill="blue", outline="black")

        # Also draw it in Canvas 2 for modification
        self.canvas2.delete("all")
        self.polygon2 = self.canvas2.create_polygon(self.vertices, fill="blue", outline="black")

    def on_click(self, event):
        """Handle point-and-click modification on Canvas 2"""
        # Find the closest vertex to the click and start dragging it
        pass  # Implement logic to modify polygon points

    def on_drag(self, event):
        """Drag the polygon points around the canvas"""
        pass  # Implement logic to dynamically move polygon points

    def save_layout(self):
        """Save the current polygon and parameters to a file"""
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, "w") as f:
                f.write(f"Number of Sides: {self.num_sides_entry.get()}\n")
                f.write(f"Polygon Size: {self.size_entry.get()}\n")
                f.write(f"Vertices: {self.vertices}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = SRGApp(root)
    root.mainloop()
