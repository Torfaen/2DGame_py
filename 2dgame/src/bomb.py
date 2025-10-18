import pygame
import os

TILE_SIZE=32
FPS=60
class Bomb(pygame.sprite.Sprite):
    def __init__(self, x, y, power, color=(173, 216, 230)):
        #基础属性
        super().__init__()  # 调用父类初始化
        self.image = pygame.Surface((20, 20))  # 或使用实际图像
        self.image.fill(color)  # 临时填充颜色
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        #泡泡爆炸相关
        self.power = power
        self.timer = 0
        self.exploded = False
        #泡泡爆炸动画持续时间
        self.explosion_timer = 0
        # 是否为连锁爆炸
        self.is_chain_reaction = False
        # 加载各个状态的图像
        self.images = {
            "center":None,
            "down": None,
            "up": None,
            "left": None,
            "right": None
        }
        #临时贴图
        bomb_path = os.path.join("..", "assets", "sprites", "bomb", "idle_0.png")
        self.image_bomb= self.load_bomb_sprite(bomb_path)

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
    def load_bomb_sprite(self,path,size=(32,32)):
        #加载泡泡贴图
        try:
            image = pygame.image.load(path)
            image = pygame.transform.scale(image,size)
            return image
        except (pygame.error, FileNotFoundError) as e:
            # 临时方块贴图
            surface = pygame.Surface(size, pygame.SRCALPHA)
            #pygame.draw.rect(self.image_bomb, (173, 216, 230), (self.rect.x, self.rect.y, 32, 32))
            pygame.draw.rect(surface, (173, 216, 230), surface.get_rect())
            print(f"警告：无法加载泡泡图片 ({e})")
            return surface

    def check_nearby_bombs(self,bombs_group):
        nearby_bombs = []
        for bomb in bombs_group:
            if bomb == self:
                continue
            # 检查未爆炸泡泡（当前泡泡）
            if not bomb.exploded:
                # 检测重叠的泡泡
                if self.rect.colliderect(bomb.rect):
                    nearby_bombs.append(bomb)
                # 检测爆炸区域的泡泡
                if self.rect.colliderect(bomb.rect):
                    nearby_bombs.append(bomb)

    def trigger_chain_explode(self, bombs_group):
        pass
    def handle_bomb_exploded(self):
        self.timer+=1
        #放泡泡到炸之前
        if self.timer >= FPS*3.5 and not self.exploded:
            self.exploded = True
            #爆炸持续时间,t/FPS=0.5s
            self.explosion_timer=30
            #连锁爆炸
#            self.trigger_chain_explode(bombs_group)

        #泡泡开炸
        if self.exploded:
            self.explosion_timer-=1
            if self.explosion_timer<=0:
                #从bomb_group中移除
                self.kill()


    def draw_bomb(self, window):
        if not self.exploded:
            window.blit(self.image_bomb, self.rect.topleft)
        else:
            #爆炸临时方块贴图
            #中心爆炸
            pygame.draw.rect(window, (255, 100, 0), (self.rect.x, self.rect.y, 32, 32))
            # 上下左右方向的爆炸
            for i in range(1, self.power + 1):
                # 上
                pygame.draw.rect(window, (255, 100, 0),
                                 (self.rect.x, self.rect.y - i * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                # 下
                pygame.draw.rect(window, (255, 100, 0),
                                 (self.rect.x, self.rect.y + i * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                # 左
                pygame.draw.rect(window, (255, 100, 0),
                                 (self.rect.x - i * TILE_SIZE, self.rect.y, TILE_SIZE, TILE_SIZE))
                # 右
                pygame.draw.rect(window, (255, 100, 0),
                                 (self.rect.x + i * TILE_SIZE, self.rect.y, TILE_SIZE, TILE_SIZE))


