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
        self.barrier_map = None
        self.collision_rects = []  # 存储所有障碍物的碰撞框
        self.barrier_rects = []
        self.floor_rects=[]
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

    def draw_debug_rect_floor(self, window, debug_mode):
        if not debug_mode:
            return
        for rect in self.floor_rects:
            pygame.draw.rect(window, "yellow", rect, 1)

    #定义锚点为左上角topleft
    def draw_debug_rect_collision(self, window, debug_mode):
        if debug_mode:
            for rect in self.collision_rects:
                pygame.draw.rect(window, (0, 0, 255), rect, 1)

    def draw_debug_rect_barrier(self, window, debug_mode):
        if debug_mode:
            '''
            for rect in self.barrier_map:
                pygame.draw.rect(window, (255, 0, 0), rect, 1)
            '''
            radius = 4
            for rect in self.barrier_rects:
                pygame.draw.circle(window, (0, 169, 255), (rect.x, rect.y), radius)

    def draw_debug_barrier_coords(self, window, debug_mode):
        if debug_mode:
            # 只在第一次调用时初始化字体和缓存
            if not hasattr(self, '_debug_coord_font'):
                self._debug_coord_font = pygame.font.Font(None, 14)
                self._debug_coord_text_cache = {}
                self._debug_coord_text_rects_cache = {}
                self._debug_coord_frame_counter = 0
            
            # 每5帧只渲染一次（但不清空已渲染的文字）
            # 不使用return，让已经渲染的文字保留
            

            for rect in self.barrier_rects:
                 
                # 计算grid坐标
                grid_x = rect.x // self.tile_size
                grid_y = rect.y // self.tile_size
                
                # 使用缓存避免重复渲染文本
                coord_text = f"({grid_x},{grid_y})"
                if coord_text not in self._debug_coord_text_cache:
                    self._debug_coord_text_cache[coord_text] = self._debug_coord_font.render(coord_text, True, (255, 255, 255))
                    text_rect = self._debug_coord_text_cache[coord_text].get_rect()
                    self._debug_coord_text_rects_cache[coord_text] = text_rect
                
                # 获取缓存的文本和矩形
                text_surface = self._debug_coord_text_cache[coord_text]
                text_rect = self._debug_coord_text_rects_cache[coord_text].copy()
                text_rect.center = (rect.x + self.tile_size // 2, rect.y + self.tile_size // 2)
                
                # 简化绘制：只绘制文本，不绘制背景
                window.blit(text_surface, text_rect)


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
        for y in range(len(self.floor_map)):
            for x in range(len(self.floor_map[y])):
                if floor_data[y][x] == "empty":
                    continue
                rect = pygame.Rect(x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size)
                self.floor_rects.append(rect)

    def set_barrier_map(self, barrier_data):
        """设置障碍物层"""
        self.barrier_map = barrier_data
        for y in range(len(self.barrier_map)):
            for x in range(len(self.barrier_map[y])):
                if barrier_data[y][x] == "empty":
                    continue
                rect = pygame.Rect(x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size)
                self.barrier_rects.append(rect)

    #障碍物破坏部分函数
    def remove_barrier(self, x, y):
        #二维数组索引，先行后列y 表示行号（垂直方向）x 表示列号（水平方向）
        old_obj_name=self.barrier_map[y][x]
        self.barrier_map[y][x] = "empty"
        # 移除对应的碰撞框
        target_rect = pygame.Rect(x * self.tile_size, y * self.tile_size, 
                                self.tile_size, self.tile_size)
        self.barrier_rects = [rect for rect in self.barrier_rects 
                            if not rect.collidepoint(target_rect.center)]
        print(f"remove barrier:{old_obj_name}")

    def generate_collision(self, grid_x, grid_y):
        # 先检查是否已存在相同位置的碰撞矩形，有就返回
        if any(rect.x == grid_x * self.tile_size and rect.y == grid_y * self.tile_size
               for rect in self.collision_rects):
            return
        # 确认不存在后再添加
        self.collision_map[grid_y][grid_x] = 1
        target_rect = pygame.Rect(grid_x * self.tile_size, grid_y * self.tile_size,
                                  self.tile_size, self.tile_size)
        self.collision_rects.append(target_rect)

    def remove_collision(self, grid_x, grid_y):
        self.collision_map[grid_y][grid_x] = 0
        target_rect = pygame.Rect(grid_x * self.tile_size, grid_y * self.tile_size,
                                  self.tile_size, self.tile_size)
        self.collision_rects=[rect for rect in self.collision_rects 
                            if not rect.collidepoint(target_rect.center)]
                            
    def draw_tile(self, window, tile_name, x, y):
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
            print(f"没有找到名为 {tile_name} 的贴图")
            return
        image = self.tiles[tile_name]
        # 底部对齐
        draw_x = x
        draw_y = y  - (image.get_height() - self.tile_size)
        window.blit(image, (draw_x, draw_y))


    def draw_floor(self, window):
        """按照JSON中地板配置绘制地板层"""
        if not self.floor_map:
            print("没有地板数据")
            return
        for y in range(len(self.floor_map)):
            for x in range(len(self.floor_map[y])):
                tile_name = self.floor_map[y][x]
                screen_x = x * self.tile_size
                screen_y = y * self.tile_size

                self.draw_tile(window, tile_name, screen_x, screen_y)


    def draw_barrier_layer(self, window):
        """绘制障碍物层"""
        if not self.barrier_map:
            return
        for y in range(len(self.barrier_map)):
            for x in range(len(self.barrier_map[y])):
                tile_name = self.barrier_map[y][x]
                #if tile_name in self.block_tiles:
                self.draw_tile(window,tile_name, x , y )
