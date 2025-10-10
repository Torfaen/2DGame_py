import pygame
from os.path import isfile, join
class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface([width, height],pygame.SRCALPHA)
        self.name = name
        self.width= width
        self.height= height
        self.name= name

    def draw(self, win):
#       初期调试用代码
#       pygame.draw.rect(win,self.COLOR,self.rect)
#       self.sprite=self.SPRITES["idle_"+self.direction ][0]
        win.blit(self.image, (self.rect.x,  self.rect.y))

class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block=get_block(size)
        self.image.blit(block,(0,0))
        #会根据self.image表面的像素信息生成一个掩码对象，用于更精确的像素级碰撞检测。
        self.mask=pygame.mask.from_surface(self.image)

def get_block(size):
    #路径
    path=join("assets","Terrain","Terrain.png")
    #有路径后，用pygame包加载它
    image=pygame.image.load(path).convert_alpha()
    #创建一个surface用于表示图像，即为画布
    surface=pygame.Surface((size,size),pygame.SRCALPHA,32)
    #创建一个rectangle，用于选取terrain的方块
    rect=pygame.Rect(96,0,size,size)
    #把选取的方块画在画布上
    surface.blit(image,(0,0),rect)
    return pygame.transform.scale2x(surface)