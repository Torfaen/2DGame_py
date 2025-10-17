import pygame
import os

FPS=60
class Bomb(pygame.sprite.Sprite):
    def __init__(self, grid_x, grid_y, power, color=(173, 216, 230)):
        #基础属性
        super().__init__()  # 调用父类初始化
        self.image = pygame.Surface((20, 20))  # 或使用实际图像
        self.image.fill(color)  # 临时填充颜色
        self.rect = self.image.get_rect()
        self.rect.x = grid_x
        self.rect.y = grid_y
        #泡泡爆炸相关
        self.power = power
        self.timer = 0
        self.exploded = False
        #泡泡爆炸动画持续时间
        self.explosion_timer = 0

        # 加载各个状态的图像
        self.images = {
            "center":None,
            "down": None,
            "up": None,
            "left": None,
            "right": None
        }
        #加载泡泡贴图
        try:
            shadow_path = os.path.join("..", "assets", "sprites", "bomb", "idle_0.png")
            self.image_bomb = pygame.image.load(shadow_path)
            #self.image_shadow = pygame.transform.scale(self.image_shadow, (50, 20))  # 按需缩放
        except (pygame.error, FileNotFoundError) as e:
            self.image_bomb = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.circle(self.image_bomb, (173, 216, 230), (10, 10), 13)
            print(f"警告：无法加载泡泡图片 ({e})")

    def handle_bomb(self):
        self.timer+=1
        if self.timer >= FPS*3.5:
            self.exploded = True
            self.explosion_timer=30

    def draw_bomb(self, window):
        window.blit(self.image_bomb, self.rect.topleft)

