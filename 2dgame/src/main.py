import os
from http.cookiejar import join_header_words

import pygame
from player import Player
from map import  Map
import json
# 设置窗口，全局参数设置
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
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
        "right": pygame.K_RIGHT
    }
    player2_controls = {
        "up": pygame.K_w,
        "down": pygame.K_s,
        "left": pygame.K_a,
        "right": pygame.K_d
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
        x=400,
        y=300,
        controls=player2_controls,
        #读取贴图错误时使用红方块代替
        color=(255, 0, 0)  # 红色
    )

    # 主游戏循环
    running = True
    while running:
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 获取玩家的 Y 坐标
        player_y = player.y
        player2_y = player2.y
        # 更新玩家移动
        player.move(0, 0)  # 调用移动方法
        player2.move(0, 0)
        # 绘制
        window.fill((0, 0, 0))  # 清屏（黑色背景）
        '''
        #初版逻辑，没有锚点遮挡关系
        map_obj.draw_floor(window)

        map_obj.draw_visual_layer(window)

        player.draw(window)
        '''
        map_obj.draw_floor(window)

        # 把可遮挡的物体（房子）和玩家一起放到一个列表
        drawables = []

        # 把地图物件加入列表
        for y in range(len(map_obj.visual_map)):
            for x in range(len(map_obj.visual_map[y])):
                tile_name = map_obj.visual_map[y][x]
                if tile_name in map_obj.block_tiles:
                    # 获取每个物件的绘制坐标（房子的底部在 tile_y + tile_size）
                    pos_x = x * map_obj.tile_size
                    pos_y = y * map_obj.tile_size
                    feet_y = pos_y + map_obj.tile_size  # 假设 tile 高度=底部锚点
                    drawables.append(("tile", tile_name, pos_x, pos_y, feet_y))

        # 加入玩家
        drawables.append(("player", player, player.x, player.y, player.y + 64))  # 64是角色高度
        drawables.append(("player", player2, player2.x, player2.y, player2.y + 64))
        # 按 feet_y 排序
        drawables.sort(key=lambda obj: obj[4])

        # 依次绘制
        for obj in drawables:
            kind = obj[0]
            if kind == "tile":
                _, tile_name, x, y, _ = obj
                map_obj.draw_tile(window, tile_name, x, y)
            elif kind == "player":
                _, p, _, _, _ = obj
                p.draw(window)

        # 更新显示
        pygame.display.update()
        clock.tick(60)  # 60 FPS

    # 退出Pygame
    pygame.quit()


if __name__ == "__main__":
    main()
