# 在 map.py 文件中创建 Map 类
import pygame
import os
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

import pygame
import os

class SpriteSheet:
    def __init__(self, path):
        try:
            # 加载精灵表
            self.sheet = pygame.image.load(path).convert_alpha()
        except pygame.error:
            print(f"无法加载精灵表: {path}")
            self.sheet = None

    def get_sprite(self, x, y, width, height):
        """从精灵表中提取指定位置的精灵"""
        if not self.sheet:
            return None
        # 创建新的表面
        sprite = pygame.Surface((width, height), pygame.SRCALPHA)
        # 从精灵表中复制指定区域
        sprite.blit(self.sheet, (0, 0), (x, y, width, height))
        return sprite



class Map:
    def __init__(self):
        self.tile_size=32
        self.collision_map = None
        self.floor_map= None
        self.visual_map = None
        self.collision_rects = []  # 存储所有障碍物的碰撞框

        # 贴图字典，用于自动加载文件夹内贴图,全部存入 self.tiles
        self.tiles = {}
        tiles_path = os.path.join("..", "assets", "sprites", "background","map_base")
        for filename in os.listdir(tiles_path):
            if filename.endswith(".png"):
                # 去掉扩展名
                name = os.path.splitext(filename)[0]
                img_path = os.path.join(tiles_path, filename)
                self.tiles[name] = pygame.image.load(img_path).convert_alpha()

    '''老的贴图加载方式，弃用
        # 创建精灵表对象
        sprite_sheet = SpriteSheet(os.path.join("..","assets", "sprites", "background", "map_base", "obj.png"))
        # 提取不同元素
        # 草地 (0,0) - 32x32
        self.grass = sprite_sheet.get_sprite(0, 0, 32, 32)
        # 树木 (0,32) - 32x32
#        self.tree = sprite_sheet.get_sprite(32, 32, 32, 32)
        # 房屋 (32,0) - 32x32
        self.house = sprite_sheet.get_sprite(32, 0, 32, 64)
        # 水 (32,32) - 32x32
        self.water = sprite_sheet.get_sprite(32, 32, 32, 32)
    '''



    def draw_debug_rect_collision(self, window, debug_mode):
        if debug_mode:
            for rect in self.collision_rects:
                pygame.draw.rect(window, (0, 0, 255), rect, 1)
    def set_collision_map(self, collision_data):
        """设置碰撞层"""
        self.collision_map = collision_data
        for y, row in enumerate(collision_data):
            for x, value in enumerate(row):
                if value == 1:  # 有碰撞
                    rect = pygame.Rect(x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size)
                    self.collision_rects.append(rect)

    def set_floor_map(self, floor_data):
        """设置地板层"""
        self.floor_map = floor_data

    def set_visual_map(self, visual_data):
        """设置表现层"""
        self.visual_map = visual_data

    def draw_tile(self, window, tile_name, grid_x, grid_y):
        '''老的绘制贴图方式
        """绘制指定类型的瓷砖,在指定的坐标（x，y）"""
        draw_x = x * self.tile_size
        draw_y = y * self.tile_size - (tile_name.get_height() - self.tile_size)

        if tile_name == "grass":
            window.blit(self.grass, (draw_x, draw_y))
        elif tile_name == "tree":
            window.blit(self.tree, (draw_x, draw_y))
        elif tile_name == "house":
            window.blit(self.house, (draw_x, draw_y))
        elif tile_name == "water":
            window.blit(self.water, (draw_x, draw_y))
        '''
        if tile_name not in self.tiles :
#            print(f"没有找到名为 {tile_name} 的贴图")
            return
        image = self.tiles[tile_name]
        # 底部对齐
        draw_x = grid_x * self.tile_size
        draw_y = grid_y * self.tile_size - (image.get_height() - self.tile_size)
        window.blit(image, (draw_x, draw_y))
    def draw_floor(self, window):
        """按照JSON中地板配置绘制地板层"""
        if not self.floor_map:
            print("没有地板数据")
            return
        for y in range(len(self.floor_map)):
            for x in range(len(self.floor_map[y])):
                tile_name = self.floor_map[y][x]
 #               screen_x = x * self.tile_size
 #               screen_y = y * self.tile_size
                #只传格子坐标，像素计算全部在draw_tile中完成
                self.draw_tile(window, tile_name, x, y)


    def draw_visual_layer(self, window):
        """绘制表现层"""
        if not self.visual_map:
            return
        for y in range(len(self.visual_map)):
            for x in range(len(self.visual_map[y])):
                tile_name = self.visual_map[y][x]
                #if tile_name in self.block_tiles:
                self.draw_tile(window,tile_name, x , y )
