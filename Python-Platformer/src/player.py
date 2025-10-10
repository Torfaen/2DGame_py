import pygame
import sprite
class Player(pygame.sprite.Sprite):
    COLOR=(255,0,0)
    GRAVITY=1

    SPRITES= sprite.load_sprite_sheets("MainCharacters", "MaskDude", 32, 32, True)

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
        #self.y_vel+=min(1, (self.fall_count/fps)*self.GRAVITY)
        self.move(self.x_vel, self.y_vel)
        self.fall_count+=1

    def draw(self, win):
#       初期调试用代码
#        pygame.draw.rect(win,self.COLOR,self.rect)
        self.sprite=self.SPRITES["idle_"+self.direction ][0]
        win.blit(self.sprite, (self.rect.x,  self.rect.y))
