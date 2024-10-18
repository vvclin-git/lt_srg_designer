import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

class PolygonPatch:
    def __init__(self, ax, points, color):
        self.points = points
        self.color = color
        self.polygon = patches.Polygon(points, closed=True, color=color)
        self.ax = ax
        self.ax.add_patch(self.polygon)
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0

    def update_polygon(self, points):
        self.polygon.set_xy(points)
        self.ax.figure.canvas.draw()

    def on_press(self, event):
        if self.polygon.contains_point((event.x, event.y)):
            self.dragging = True
            self.offset_x = self.polygon.xy[0, 0] - event.xdata
            self.offset_y = self.polygon.xy[0, 1] - event.ydata

    def on_release(self, event):
        self.dragging = False

    def on_motion(self, event):
        if self.dragging:
            dx = event.xdata + self.offset_x
            dy = event.ydata + self.offset_y
            new_points = self.points + np.array([dx - self.points[0][0], dy - self.points[0][1]])
            self.update_polygon(new_points)
            self.points = new_points

def on_press(event):
    for patch in patches_list:
        patch.on_press(event)

def on_release(event):
    for patch in patches_list:
        patch.on_release(event)

def on_motion(event):
    for patch in patches_list:
        patch.on_motion(event)

fig, ax = plt.subplots()
ax.set_xlim(0, 800)
ax.set_ylim(0, 800)

# 定義顏色
BLUE = 'blue'
RED = 'red'

# 創建多邊形
polygon1_points = np.array([(0, 0), (100.5, 0), (100, 100), (0, 100)])
polygon2_points = np.array([(400, 100), (500, 150), (450, 250), (350, 250)])
patches_list = [PolygonPatch(ax, polygon1_points, BLUE), PolygonPatch(ax, polygon2_points, RED)]

fig.canvas.mpl_connect('button_press_event', on_press)
fig.canvas.mpl_connect('button_release_event', on_release)
fig.canvas.mpl_connect('motion_notify_event', on_motion)

plt.show()
