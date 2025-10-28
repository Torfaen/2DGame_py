import os

import pygame
from player import Player
from map import  Map
import json

# 设置窗口，全局参数设置
from config_loader import load_config, dict_controls
config=load_config()

WINDOW_WIDTH=config['windows']['window']['width']
WINDOW_HEIGHT=config['windows']['window']['height']
DEBUG_MODE=config['windows']['debug']['DEBUG_MODE']
GAMEMODE=config['game']['modes_allowed']
CURRENT_GAME_MODE=config['game']['current_mode']

'''弃用硬编码，使用配置文件
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
DEBUG_MODE= False
GAMEMODE=["POINT","ONE_LIFE"]
'''
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
    global DEBUG_MODE
    # 初始化Pygame
    pygame.init()
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Player Movement Test")

    # 地图路径
    base_dir = config['assets']['base_dir']
    maps_config = config['assets']['maps']
    active_map_id = config['map']['active_id']
    
    floor_map_path = os.path.join(base_dir, maps_config['floor'])
    barrier_map_path = os.path.join(base_dir, maps_config['barrier'])
    collision_map_path = os.path.join(base_dir, maps_config['collision'])
    
    floor_map = load_map_path(floor_map_path, active_map_id)
    barrier_map = load_map_path(barrier_map_path, active_map_id)
    collision_map = load_map_path(collision_map_path, active_map_id)

    # 创建地图对象
    map_obj = Map()
    map_obj.set_floor_map(floor_map)
    map_obj.set_collision_map(collision_map)
    map_obj.set_barrier_map(barrier_map)

    # 设置时钟
    clock = pygame.time.Clock()

    # 创建玩家对象
    player_1_config = config['players'][0]
    player_2_config = config['players'][1]
    player_controls = dict_controls(player_1_config['controls'])
    player2_controls = dict_controls(player_2_config['controls'])
    
    player = Player(
        #读取config
        id=player_1_config['id'],
        controls=player_controls,
        speed=player_1_config['speed'],
        speed_max=player_1_config['speed_max'],
        bombs_count=player_1_config['bomb_count'],
        bombs_max=player_1_config['bomb_max'],
        bomb_power=player_1_config['bomb_power'],
        bomb_power_max=player_1_config['bomb_power_max'],
        #读取贴图错误时使用红方块代替
        color=(255, 0, 0),
        game_mode=CURRENT_GAME_MODE,
        # 日后修改为传参
        x=player_1_config['spawn']['x'],
        y=player_1_config['spawn']['y'],
        sprite_name=config['assets']['sprites_name']['player_4'],

    )
    player2 = Player(
        id=player_2_config['id'],
        controls=player2_controls,
        speed=player_2_config['speed'],
        speed_max=player_2_config['speed_max'],
        bombs_count=player_2_config['bomb_count'],
        bombs_max=player_2_config['bomb_max'],
        bomb_power=player_2_config['bomb_power'],
        bomb_power_max=player_2_config['bomb_power_max'],
        color=(255, 0, 0),
        game_mode=CURRENT_GAME_MODE,
        # 日后修改为传参
        x=player_2_config['spawn']['x'],
        y=player_2_config['spawn']['y'],
        sprite_name=config['assets']['sprites_name']['player_1'],
    )
    '''弃用硬编码，使用配置文件
    player2 = Player(
        id=2,
        x=200,
        y=100,
        controls=player2_controls,
        #读取贴图错误时使用红方块代替
        color=(255, 0, 0),  # 红色
        sprite_name="player1_sprite",
        game_mode=CURRENT_GAME_MODE
    )
    '''
    # 创建炸弹组
    bombs_group = pygame.sprite.Group()
    # 创建玩家组
    players_group = pygame.sprite.Group()
    players_group.add(player, player2)


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
        # 更新玩家移动
        for player_obj in players_group:
            #玩家动作
            player_obj.move(map_obj.collision_rects)
            player_obj.place_bomb(bombs_group,map_obj)
            #玩家状态
            player_obj.update()
        # 泡泡列表信息更新
        for bomb in list(bombs_group):
            bomb.handle_bomb_exploded()
             # 处理爆炸逻辑
            if bomb.exploded and bomb.explosion_timer >= 29 and not bomb.explosion_handled:  # 刚爆炸时且未处理过
                bomb.handle_explosion(bombs_group,players_group)

            for player_obj in players_group:
                if player_obj.ifInExplosion(bomb.explosion_rect):
                    player_obj.hit_by_bomb(CURRENT_GAME_MODE)

        '''
        # 碰撞系统调试
        # 碰撞检测（已注释，因为移动逻辑中已处理）
        # for block in map_obj.collision_rects:
        #     if player.feet_rect.colliderect(block)or player2.feet_rect.colliderect(block):
        #         pass
        '''
        # 绘制画面
        window.fill((0, 0, 0))  # 清屏（黑色背景）
        '''
        #初版逻辑，没有锚点遮挡关系
        map_obj.draw_floor(window)

        map_obj.draw_barrier_layer(window)

        player.draw(window)
        '''
        map_obj.draw_floor(window)
        #一次画完表现层
#       map_obj.draw_barrier_layer(window)

        # 把可遮挡的物体（房子）和玩家一起放到一个列表
        drawables = []

        # 把地图物件加入列表
        for y in range(len(map_obj.barrier_map)):
            for x in range(len(map_obj.barrier_map[y])):
                if map_obj.barrier_map[y][x]=="empty":
                    continue
                tile_name = map_obj.barrier_map[y][x]
#                if tile_name in map_obj.block_tiles:
                    # 获取每个物件的绘制坐标（房子的底部在 tile_y + tile_size）
                pos_x = x * map_obj.tile_size
                pos_y = y * map_obj.tile_size
                # tile 高度=底部锚点
                feet_y = pos_y + map_obj.tile_size
                drawables.append(("tile", tile_name, pos_x, pos_y, feet_y))

        # 加入玩家
        for player_obj in players_group:
            drawables.append(("player", player_obj, player_obj.rect.x, player_obj.rect.y, player_obj.feet_rect.y))
        # 加入泡泡
        for bomb in bombs_group:
            drawables.append(("bomb", bomb, bomb.rect.x, bomb.rect.y, bomb.rect.y))

        # 调试：print(drawables)
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
                bomb_obj.draw(window)  # 传入地图对象用于爆炸范围计算

        # 绘制调试信息（在绘制完所有游戏对象之后，避免在循环内重复绘制）
        if DEBUG_MODE:
            map_obj.draw_debug_rect_barrier(window, DEBUG_MODE)
            map_obj.draw_debug_barrier_coords(window, DEBUG_MODE)  # 显示barrier坐标
            map_obj.draw_debug_rect_collision(window, DEBUG_MODE)
            for player_obj in players_group:
                player_obj.draw_debug_rect(window, DEBUG_MODE)

        # 更新显示
        pygame.display.update()
        clock.tick(60)  # 60 FPS

    # 退出Pygame
    pygame.quit()


if __name__ == "__main__":
    main()
