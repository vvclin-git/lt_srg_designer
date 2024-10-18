import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# 定義立方體的頂點
vertices = [
    [1, 0.5, -1],
    [1, -0.5, -1],
    [-1, -0.5, -1],
    [-1, 0.5, -1],
    [1, 0.5, 1],
    [1, -0.5, 1],
    [-1, -0.5, 1],
    [-1, 0.5, 1]
]

# 定義立方體的邊
edges = [
    [0, 1],
    [1, 2],
    [2, 3],
    [3, 0],
    [4, 5],
    [5, 6],
    [6, 7],
    [7, 4],
    [0, 4],
    [1, 5],
    [2, 6],
    [3, 7]
]

# 定義立方體的面
surfaces = [
    [0, 1, 2, 3],
    [4, 5, 6, 7],
    [0, 1, 5, 4],
    [2, 3, 7, 6],
    [0, 3, 7, 4],
    [1, 2, 6, 5]
]

# 定義顏色
colors = [
    [1, 0, 0, 0.5], # 半透明紅色
    [0, 1, 0, 0.5], # 半透明綠色
    [0, 0, 1, 0.5], # 半透明藍色
    [1, 1, 0, 0.5], # 半透明黃色
    [1, 0, 1, 0.5], # 半透明紫色
    [0, 1, 1, 0.5]  # 半透明青色
]

def draw_cube():
    glBegin(GL_QUADS)
    for i, surface in enumerate(surfaces):
        glColor4fv(colors[i])
        for vertex in surface:
            glVertex3fv(vertices[vertex])
    glEnd()

    glColor3fv((0, 0, 0))
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -5)

    # 启用混合和設置混合函數以實現半透明效果
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # 設置背景顏色為白色
    glClearColor(1, 1, 1, 1)

    # 設置初始視角
    x_rot = 0
    y_rot = 0
    zoom = -5  # 初始縮放，控制物體距離

    # 隱藏滑鼠光標並捕捉滑鼠移動
    #pygame.mouse.set_visible(False)
    #pygame.event.set_grab(True)
    dragging = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            # 處理滾輪事件進行縮放
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # 滾輪向上滾動，放大
                    zoom += 0.5
                elif event.button == 5:  # 滾輪向下滾動，縮小
                    zoom -= 0.5
        
        # 檢查滑鼠按鍵狀態
        mouse_buttons = pygame.mouse.get_pressed()

        if mouse_buttons[0] and not dragging:
            pygame.mouse.get_rel()
            dragging = True
        elif mouse_buttons[0] and dragging:
            pass
        else:
            dragging = False


        # 如果正在拖曳，則根據滑鼠移動量旋轉
        if dragging:
            # 獲取滑鼠移動量
            mouse_dx, mouse_dy = pygame.mouse.get_rel()
            x_rot += mouse_dy * 0.2
            y_rot += mouse_dx * 0.2

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
        glTranslatef(0.0, 0.0, zoom)
        glRotatef(x_rot, 1, 0, 0)
        glRotatef(y_rot, 0, 1, 0)

        draw_cube()
        pygame.display.flip()
        pygame.time.wait(10)                



if __name__ == "__main__":
    main()