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
        # 创建精灵表对象
        sprite_sheet = SpriteSheet(os.path.join("..","assets", "sprites", "background", "map_base", "obj.png"))
        # 提取不同元素
        # 草地 (0,0) - 32x32
        self.grass = sprite_sheet.get_sprite(0, 0, 32, 32)
        # 树木 (0,32) - 32x32
        self.tree = sprite_sheet.get_sprite(0, 32, 32, 32)
        # 房屋 (32,0) - 32x32
        self.house = sprite_sheet.get_sprite(32, 0, 32, 64)
        # 水 (32,32) - 32x32
        self.water = sprite_sheet.get_sprite(32, 32, 32, 32)

    def draw_tile(self, window, tile_type, x, y):
        """绘制指定类型的瓷砖"""
        if tile_type == "grass":
            window.blit(self.grass, (x, y))
        elif tile_type == "tree":
            window.blit(self.tree, (x, y))
        elif tile_type == "house":
            window.blit(self.house, (x, y))
        elif tile_type == "water":
            window.blit(self.water, (x, y))



