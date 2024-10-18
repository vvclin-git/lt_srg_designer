import pygame
import pygame_gui
import numpy as np

WHITE = (255, 255, 255)
BLACK = (0, 0, 0) 
BLUE = (0, 0, 255, 50)
RED = (255, 0, 0, 50)
GREY_D = (100, 100, 100)
GREY_L = (200, 200, 200)

WIDTH, HEIGHT = 800, 600
F_WIDTH = min(WIDTH, HEIGHT)
P_WIDTH = 0.8*F_WIDTH

class PolygonSprite(pygame.sprite.Sprite):
    def __init__(self, points, color):
        super().__init__()
        self.points = points
        self.color = color
        self.image = self.create_image()
        self.rect = self.image.get_rect()
        self.rect.topleft = (points[0][0], points[0][1])
        self.dragging = False
        self.shift = (F_WIDTH-P_WIDTH)/2

    def create_image(self):
        min_x = min(point[0] for point in self.points)
        min_y = min(point[1] for point in self.points)
        max_x = max(point[0] for point in self.points)
        max_y = max(point[1] for point in self.points)
        width = max_x - min_x
        height = max_y - min_y
        image = pygame.Surface((width, height), pygame.SRCALPHA)
        translated_points = [(x - min_x, y - min_y) for x, y in self.points]
        pygame.draw.polygon(image, self.color, translated_points)
        return image

    def update(self):
        if self.dragging:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.rect.topleft = (mouse_x + self.offset_x, mouse_y + self.offset_y)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint((event.pos[0]-self.shift, event.pos[1]-self.shift)):
                self.dragging = True
                mouse_x, mouse_y = event.pos
                self.offset_x = self.rect.x - mouse_x
                self.offset_y = self.rect.y - mouse_y
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

class FakeMatplot():
    def __init__(self, width, height, xticks = 5, yticks = 5):
        self.width, self.height = width, height
        self.p_square = 0.8 * max([width, height])
        self.center = width / 2, height / 2
        self.xticks, self.yticks = xticks ,yticks
        self.screen = pygame.Surface((width, height), pygame.SRCALPHA)
        self.plot = pygame.Surface((self.p_square, self.p_square), pygame.SRCALPHA)
        self.rect = self.plot.get_rect()
        self.rect.x = (width-self.p_square)/2
        self.rect.y = (height-self.p_square)/2
        
        self.screen.fill(WHITE)
        frame = [(self.center[0] - self.p_square/2, self.center[1] - self.p_square/2), 
                 (self.center[0] - self.p_square/2, self.center[1] + self.p_square/2), 
                 (self.center[0] + self.p_square/2, self.center[1] + self.p_square/2), 
                 (self.center[0] + self.p_square/2, self.center[1] - self.p_square/2)]
        xaxis = [(self.center[0] - self.p_square/2,self.center[1]),(self.center[0] + self.p_square/2,self.center[1])]
        yaxis = [(self.center[0],self.center[1] - self.p_square/2),(self.center[0],self.center[1] + self.p_square/2)]
        pygame.draw.lines(self.screen, BLACK, True, frame, width=2)
        pygame.draw.line(self.screen, BLACK, xaxis[0],xaxis[1], width=2)
        pygame.draw.line(self.screen, BLACK, *yaxis, width=2)
        self.draw_grid()

    def draw_grid(self, color = GREY_L, width = 1, xticks = 5, yticks = 5):
        for xi in np.linspace(-self.p_square/2, self.p_square/2, 2 * xticks + 1):
            pygame.draw.line(self.screen, color, (self.center[0] + xi, self.center[1] - self.p_square/2), (self.center[0] + xi, self.center[1] + self.p_square/2), width=width)
        for yi in np.linspace(-self.p_square/2, self.p_square/2, 2 * yticks + 1):
            pygame.draw.line(self.screen, color, (self.center[0] - self.p_square/2, self.center[1] - yi), (self.center[0] + self.p_square/2, self.center[1] - yi), width=width)

pygame.init()
pygame.font.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
figure = FakeMatplot(F_WIDTH, F_WIDTH)
control_screen = pygame.Surface((WIDTH-F_WIDTH, F_WIDTH))
pygame.display.set_caption('K-Domain')

polygon1_points = [(100, 100), (200, 50), (300, 100), (250, 200), (150, 200)]
polygon2_points = [(400, 100), (500, 150), (450, 250), (350, 250)]
polygon1 = PolygonSprite(polygon1_points, BLUE)
polygon2 = PolygonSprite(polygon2_points, RED)

object_sprites = pygame.sprite.Group()
object_sprites.add(polygon1)
object_sprites.add(polygon2)

manager = pygame_gui.UIManager((WIDTH, HEIGHT))

# Add a button
draw_circle_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((WIDTH-200, 50), (150, 50)),
                                                  text='Draw Circle',
                                                  manager=manager)

running = True
clock = pygame.time.Clock()

while running:
    time_delta = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if figure.rect.collidepoint((event.pos[0], event.pos[1])):
                print(event.pos)
        if event.type == pygame.USEREVENT:
            if manager.process_events(event):
                if event.ui_element == draw_circle_button:
                    pygame.draw.circle(figure.plot, BLACK, (figure.p_square // 2, figure.p_square // 2), 50)

        for sprite in object_sprites:
            sprite.handle_event(event)

        manager.process_events(event)

    control_screen.fill(GREY_D)
    figure.plot.fill((0, 0, 0, 50))

    object_sprites.update()
    object_sprites.draw(figure.plot)

    manager.update(time_delta)

    screen.blit(figure.screen, (0, 0))
    screen.blit(control_screen, (F_WIDTH, 0))
    screen.blit(figure.plot, ((F_WIDTH-P_WIDTH)/2+1, (F_WIDTH-P_WIDTH)/2+1))
    manager.draw_ui(screen)

    pygame.display.flip()

pygame.quit()
