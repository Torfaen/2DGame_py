import pygame
from player import Player
from map import  Map
# 设置窗口，全局参数设置
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600


def main():
    # 初始化Pygame
    pygame.init()
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Player Movement Test")

    # 创建地图对象
    map_obj = Map()

    # 设置时钟
    clock = pygame.time.Clock()

    # 创建玩家对象
    player_controls = {
        "up": pygame.K_UP,
        "down": pygame.K_DOWN,
        "left": pygame.K_LEFT,
        "right": pygame.K_RIGHT
    }

    player = Player(
        id=1,
        x=400,
        y=300,
        controls=player_controls,
        color=(255, 0, 0)  # 红色
    )

    # 主游戏循环
    running = True
    while running:
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False


        # 更新玩家移动
        player.move(0, 0)  # 调用移动方法

        # 绘制
        window.fill((0, 0, 0))  # 清屏（黑色背景）
        map_obj.draw_tile(window,"house", 0, 0) # 绘制地图
        player.draw(window)  # 绘制玩家


        # 更新显示
        pygame.display.update()
        clock.tick(60)  # 60 FPS

    # 退出Pygame
    pygame.quit()


if __name__ == "__main__":
    main()
