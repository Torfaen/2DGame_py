from re import S
import pygame
import os
from explosion import Explosion
from macholib.ptypes import sizeof
from config_loader import load_config, dict_controls

config=load_config()
TILE_SIZE=config["windows"]["tile_size"]
FPS=config["windows"]["fps"]
#泡泡类，一个类对象，用于管理一个泡泡
class Bomb(pygame.sprite.Sprite):
    def __init__(self, x, y, power, color=(173, 216, 230),map_obj=None):
        #基础属性
        super().__init__()  # 调用父类初始化
        self.explosion_rect = []
        self.image = pygame.Surface((20, 20))  # 或使用实际图像
        self.image.fill(color)  # 临时填充颜色
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        #地图对象
        self.map_obj = map_obj
        # 炸弹放置时,创建阻挡
        if self.map_obj:
            self._generate_collision(x,y)
        #泡泡爆炸相关
        self.power = power
        self.timer = 0
        self.exploded = False
        #破坏的方块列表
        self.destroyed_blocks = []
        #爆炸波及的区域rect,一个泡泡对于一个爆炸区域，主函数创造一个group存储所有爆炸区域
        self.explosion_area = []
        #泡泡爆炸动画持续时间
        self.explosion_timer = 0
        # 是否已经处理过爆炸逻辑
        self.explosion_handled = False

        # 动画相关属性（必须在加载贴图前初始化）
        self.bomb_frame_index = 0
        self.bomb_frame_counter = 0
        # 每15帧换一次贴图（60 FPS 下约 4 次/秒）
        self.ANIMATION_DELAY = 15
        
        # 加载各个状态泡泡的图像
        self.image_bomb = self._load_bomb_sprite()

        # 加载各个方向爆炸水柱贴图
        self.explosion_images = {
            "center": self._load_explosion_sprite("center"),
            "up": self._load_explosion_sprite("up"),
            "down": self._load_explosion_sprite("down"),
            "left": self._load_explosion_sprite("left"),
            "right": self._load_explosion_sprite("right"),
        }
    # 放置时产生阻挡
    def _generate_collision(self,x,y):
        grid_x = x // TILE_SIZE
        grid_y = y // TILE_SIZE
        self.map_obj.generate_collision(grid_x,grid_y)
    
    # 爆炸时移除阻挡
    def remove_collision(self, x, y):
        grid_x = x // TILE_SIZE
        grid_y = y // TILE_SIZE
        self.map_obj.remove_collision(grid_x,grid_y)


        '''类内初始化贴图，已弃用
        #加载泡泡贴图
        try:
            shadow_path = os.path.join("..", "assets", "sprites", "bomb", "idle_0.png")
            self.image_bomb = pygame.image.load(shadow_path)
            #self.image_shadow = pygame.transform.scale(self.image_shadow, (50, 20))  # 按需缩放
        except (pygame.error, FileNotFoundError) as e:
            self.image_bomb = pygame.Surface((40, 40), pygame.SRCALPHA)
            #临时方块贴图
            #pygame.draw.rect(self.image_bomb, (173, 216, 230), (self.rect.x, self.rect.y, 32, 32))
            pygame.draw.circle(self.image_bomb, (173, 216, 230), (10, 10), 13)
            print(f"警告：无法加载泡泡图片 ({e})")
        '''


    def _load_explosion_sprite(self,direction,is_end=False):
        size=(32,32)
        # 判断中心
        if direction == "center":
            path=os.path.join("..", "assets", "sprites", "bomb", "center.png")
            image=pygame.image.load(path)
            image = pygame.transform.scale(image,(32,32))
            return image
        # 判断四周爆炸
        if is_end:
            path=os.path.join("..", "assets", "sprites", "bomb", "explosion_1.png")
        else:
            path=os.path.join("..", "assets", "sprites", "bomb", "explosion_0.png")
        #加载泡泡贴图
        try:
            image = pygame.image.load(path)
            if direction == "right":
                pass
            elif direction == "left":
                image = pygame.transform.flip(image, True, False)
            elif direction == "up":
                image = pygame.transform.rotate(image, 90)
            elif direction == "down":
                image = pygame.transform.rotate(image, -90)

            image = pygame.transform.scale(image,(32,32))
            return image
            

        except (pygame.error, FileNotFoundError) as e:
            # 临时方块贴图
            surface = pygame.Surface(size, pygame.SRCALPHA)
            #pygame.draw.rect(self.image_bomb, (173, 216, 230), (self.rect.x, self.rect.y, 32, 32))
            pygame.draw.rect(surface, (173, 216, 230), surface.get_rect())
            print(f"警告：无法加载泡泡图片 ({e})")
            return surface

    def _load_bomb_sprite(self):
        size=(32,32)
        path=os.path.join("..", "assets", "sprites", "bomb", f"idle_{self.bomb_frame_index}.png")
        #加载泡泡贴图
        try:
            image = pygame.image.load(path)
            image = pygame.transform.scale(image,(32,32))
            return image

        except (pygame.error, FileNotFoundError) as e:
            # 临时方块贴图
            surface = pygame.Surface(size, pygame.SRCALPHA)
            #pygame.draw.rect(self.image_bomb, (173, 216, 230), (self.rect.x, self.rect.y, 32, 32))
            pygame.draw.rect(surface, (173, 216, 230), surface.get_rect())
            print(f"警告：无法加载泡泡图片 ({e})")
            return surface

    def _update_frame_index(self):
        #动画相关
        self.bomb_frame_counter += 1
        if self.bomb_frame_counter >= self.ANIMATION_DELAY:
            self.bomb_frame_index = (self.bomb_frame_index + 1) % 4
            self.image_bomb=self._load_bomb_sprite()
            self.bomb_frame_counter = 0

    def update(self):
        #处理动画
        self._update_frame_index()
        #处理炸弹状态
        self._update_bomb_status()



    
    def get_explosion_area(self):
        explosion_area = []
        # 转换为格子坐标
        bomb_x = self.rect.x // TILE_SIZE
        bomb_y = self.rect.y // TILE_SIZE
        
        #上下左右
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]  
        #四向遍历
        for dx, dy in directions:
            for i in range(1, self.power + 1):
                check_x = bomb_x + dx * i
                check_y = bomb_y + dy * i                
                # 边界检查，地图左上角为(0,0),右下角为(len(map_obj.barrier_map[0])-1,len(map_obj.barrier_map)-1)
                # 若x<0则超左边界，x大于len(map_obj.barrier_map[0])-1则超右边界，
                # y<0则超上边界，y大于len(map_obj.barrier_map)-1则超下边界
                if (check_x < 0 or check_x >= len(self.map_obj.barrier_map[0]) or 
                    check_y < 0 or check_y >= len(self.map_obj.barrier_map)):
                    # 超出边界，跳出当前方向循环
                    break  
                # 障碍物检查
                if self.map_obj.barrier_map[check_y][check_x] != "empty":
                    # 遇到障碍物，停止该方向的爆炸
                    #self.destroyed_blocks.append((check_x, check_y))
                    #分离计算与摧毁，不然会造成贯穿摧毁
                    #map_obj.remove_barrier(check_x, check_y)
                    #map_obj.remove_collision(check_x, check_y)
                    #explosion_area.append((check_x, check_y))  # 障碍物位置也算在爆炸范围内
                    break
                #爆炸区域像素xy坐标以及rect
                self.explosion_area.append(pygame.Rect(check_x * TILE_SIZE, check_y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                #格子坐标
                explosion_area.append((check_x, check_y))
                #创建爆炸区域rect
                self.explosion_rect.append(pygame.Rect(check_x, check_y, TILE_SIZE, TILE_SIZE))
        #print("爆炸范围：", explosion_area)
        return explosion_area
    
    def _update_bomb_status(self):
        self.timer+=1
        if self.timer >= FPS*3.5 and not self.exploded:
            self.exploded = True


    def draw(self, window):
        if not self.exploded:
            window.blit(self.image_bomb, self.rect.topleft)



