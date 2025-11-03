from re import S
import pygame
import os
from explosion import Explosion
from macholib.ptypes import sizeof
from config_loader import load_config, dict_controls

config=load_config("config.yaml")
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
        self.alive = True
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

    def _update_alive(self):
        if not self.alive:
            self.kill()
            
    def update(self):
        #处理动画
        self._update_frame_index()
        #处理炸弹状态
        self._update_bomb_status()
        #处理炸弹消失
        self._update_alive()
 
    def _update_bomb_status(self):
        self.timer+=1
        if self.timer >= FPS*3.5 and not self.exploded:
            self.exploded = True

    def _update_remove(self):
            self.alive = False
            self.remove_collision(self.rect.x, self.rect.y)

    def draw(self, window):
         window.blit(self.image_bomb, self.rect.topleft)



