import pygame
from pygame.sprite import Sprite

import sprite
class Player(pygame.sprite.Sprite):
    COLOR=(255,0,0)
    GRAVITY=1
    SPRITES= sprite.load_sprite_sheets("MainCharacters", "MaskDude", 32, 32, True)
    ANIMATION_DELAY=5

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        #每帧速度
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count=0
        self.sprite = self.SPRITES["idle_left"][0]  # 设置默认精灵图像
    def move(self, dx, dy):
        self.rect.x+=dx
        self.rect.y+=dy
    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            #动画帧置0
            self.animation_count = 0
    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        #按秒算重力加速度
        self.y_vel+=min(1, (self.fall_count/fps)*self.GRAVITY)
        self.move(self.x_vel, self.y_vel)
        self.fall_count+=1
        self.update_sprite()

    def landed(self):
        #落地，重置掉落计数,y向速度，停止因为重力的加速
        self.fall_count=0
        self.y_vel=0
        self.jump_count=0

    def hit_head(self):
        self.count=0
        self.y_vel*=-1

    def update_sprite(self):
        sprite_sheet="idle"
        if self.x_vel != 0:
            sprite_sheet="run"
        sprite_shet_name=sprite_sheet+"_"+self.direction
        sprites = self.SPRITES[sprite_shet_name]
        #每五帧，展示一个不同的sprite，计算当前索引值
        sprite_index=(self.animation_count//self.ANIMATION_DELAY)%len(sprites)
        #根据计算出的索引值，从动画序列中选取对应的图像帧作为当前显示的精灵图像
        #sprites[0],sprites[1]
        self.sprite = sprites[sprite_index]
        #下一帧，播放进度+1
        self.animation_count+=1
        self.update()

    def update(self):
        #设置一个碰撞框，从左上角开始，长为贴图的长，宽为贴图的宽
        self.rect=self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask=pygame.mask.from_surface(self.sprite)

    def draw(self, win):
#       初期调试用代码
#        pygame.draw.rect(win,self.COLOR,self.rect)
#        self.sprite=self.SPRITES["idle_"+self.direction ][0]
        win.blit(self.sprite, (self.rect.x,  self.rect.y))
