import pygame
import sys

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# Define polygon points
polygon_points = [(300, 200), (400, 100), (500, 200), (450, 300), (350, 300)]
polygon_color = (0, 255, 0)  # Green

# Function to check if a point is inside a polygon
def point_in_polygon(point, polygon):
    x, y = point
    n = len(polygon)
    inside = False

    p1x, p1y = polygon[0]
    for i in range(n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside

# Variables to track dragging state
dragging = False
offset_x = 0
offset_y = 0

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            if point_in_polygon(mouse_pos, polygon_points):
                dragging = True
                # Calculate offset between mouse position and polygon's first point
                offset_x = polygon_points[0][0] - mouse_pos[0]
                offset_y = polygon_points[0][1] - mouse_pos[1]
        elif event.type == pygame.MOUSEBUTTONUP:
            dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if dragging:
                # Update polygon position based on mouse movement
                mouse_pos = event.pos
                dx = mouse_pos[0] + offset_x - polygon_points[0][0]
                dy = mouse_pos[1] + offset_y - polygon_points[0][1]
                polygon_points = [(x + dx, y + dy) for x, y in polygon_points]

    # Drawing
    screen.fill((0, 0, 0))  # Clear screen
    pygame.draw.polygon(screen, polygon_color, polygon_points)
    pygame.display.flip()
    clock.tick(60)  # Control frame rate
