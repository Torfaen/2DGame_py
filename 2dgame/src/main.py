import os

import pygame
from player import Player
from map import  Map
import json
# 设置窗口，全局参数设置
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
DEBUG_MODE= False
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 地图测试区
# 定义地图数据
#使用json导入代替
'''
visual_map = [
    ["house", "house", "house", "house"],
    ["house", "empty", "empty", "house"],
    ["house", "empty", "empty", "house"],
    ["house", "house", "house", "house"]
]
collision_map = [
    [0, 0, 0, 0],
    [0, 1, 1, 0],
    [0, 1, 1, 0],
    [0, 0, 0, 0]
]
# 创建地图对象
# map_obj = Map()
# map_obj.set_collision_map(collision_map)
# map_obj.set_visual_map(visual_map)
print("1")
'''
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def load_map_path(json_path,map_id):
    """从JSON文件加载地图数据"""
    with open(json_path, 'r', encoding='utf-8') as f:
        map_all=json.load(f)
        if map_id:
            return map_all[map_id]
        return json.load(f)

def main():
    # 声明使用全局变量
    global DEBUG_MODE
    # 初始化Pygame
    pygame.init()
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Player Movement Test")

    # 地图路径
    floor_map_path = os.path.join("..", "map", "floor_map.json")
    visual_map_path=os.path.join("..","map","visual_map.json")
    collision_map_path=os.path.join("..","map","collision_map.json")
    floor_map=load_map_path(floor_map_path,"map1")
    visual_map=load_map_path(visual_map_path,"map1")
    collision_map=load_map_path(collision_map_path,"map1")
    # 创建地图对象
    map_obj = Map()
    map_obj.set_floor_map(floor_map)
    map_obj.set_collision_map(collision_map)
    map_obj.set_visual_map(visual_map)

    # 设置时钟
    clock = pygame.time.Clock()

    # 创建玩家对象
    player_controls = {
        "up": pygame.K_UP,
        "down": pygame.K_DOWN,
        "left": pygame.K_LEFT,
        "right": pygame.K_RIGHT,
        "shift": pygame.K_RSHIFT
    }
    player2_controls = {
        "up": pygame.K_w,
        "down": pygame.K_s,
        "left": pygame.K_a,
        "right": pygame.K_d,
        "shift": pygame.K_LSHIFT
    }

    player = Player(
        id=1,
        x=400,
        y=300,
        controls=player_controls,
        #读取贴图错误时使用红方块代替
        color=(255, 0, 0)  # 红色
    )

    player2 = Player(
        id=2,
        x=200,
        y=100,
        controls=player2_controls,
        #读取贴图错误时使用红方块代替
        color=(255, 0, 0)  # 红色
    )
    # 创建炸弹组
    bombs_group = pygame.sprite.Group()



    # 主游戏循环
    running = True
    while running:
        # 处理事件
        events=pygame.event.get()
        for event in events:
            #关闭窗口
            if event.type == pygame.QUIT:
                running = False
            # 调试模式
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    DEBUG_MODE = not DEBUG_MODE
                    print(f"Debug mode: {DEBUG_MODE}")
        # 更新玩家移动
        player.move(0, 0,map_obj.collision_rects)  # 调用移动方法
        player.place_bomb(bombs_group)
        player2.move(0, 0,map_obj.collision_rects)
        player2.place_bomb(bombs_group)
        '''
        # 碰撞系统调试
        for block in map_obj.collision_rects:
            if player.feet_rect.colliderect(block)or player2.feet_rect.colliderect(block):
                print("碰到了障碍物！")
        '''
        # 绘制画面
        window.fill((0, 0, 0))  # 清屏（黑色背景）
        '''
        #初版逻辑，没有锚点遮挡关系
        map_obj.draw_floor(window)

        map_obj.draw_visual_layer(window)

        player.draw(window)
        '''
        map_obj.draw_floor(window)
        #一次画完表现层
#       map_obj.draw_visual_layer(window)

        # 把可遮挡的物体（房子）和玩家一起放到一个列表
        drawables = []

        # 把地图物件加入列表
        for y in range(len(map_obj.visual_map)):
            for x in range(len(map_obj.visual_map[y])):
                if map_obj.visual_map[y][x]=="empty":
                    continue
                tile_name = map_obj.visual_map[y][x]
#                if tile_name in map_obj.block_tiles:
                    # 获取每个物件的绘制坐标（房子的底部在 tile_y + tile_size）
                pos_x = x * map_obj.tile_size
                pos_y = y * map_obj.tile_size
                # tile 高度=底部锚点
                feet_y = pos_y + map_obj.tile_size
                drawables.append(("tile", tile_name, pos_x, pos_y, feet_y))

        # 加入玩家
        drawables.append(("player", player, player.rect.x, player.rect.y, player.rect.y + 61))  # 64是角色高度
        drawables.append(("player", player2, player2.rect.x, player2.rect.y, player2.rect.y + 61))
        # 加入泡泡
        for bomb in bombs_group:
            drawables.append(("bomb", bomb, bomb.rect.x, bomb.rect.y, bomb.rect.y))

        #        print(drawables)
        # 按 feet_y 排序
        drawables.sort(key=lambda obj: obj[4])

        # 依次绘制
        for obj in drawables:
            now_obj= obj
            kind = obj[0]
            if kind == "tile":
                _, tile_name, x, y, _ = obj
                map_obj.draw_tile(window, tile_name, x, y)
            elif kind == "player":
                _, p, _, _, _ = obj
                p.draw(window)
            elif kind == "bomb":
                _, bomb_obj, _, _, _ = obj
                bomb_obj.draw_bomb(window)  # 需要在 Bomb 类中实现 draw 方法
            # 绘制地图碰撞框
            player.draw_debug_rect(window, DEBUG_MODE)
            player2.draw_debug_rect(window, DEBUG_MODE)
            map_obj.draw_debug_rect_collision(window, DEBUG_MODE)
            map_obj.draw_debug_rect_visual(window, DEBUG_MODE)

        # 更新显示
        pygame.display.update()
        clock.tick(60)  # 60 FPS

    # 退出Pygame
    pygame.quit()


if __name__ == "__main__":
    main()
