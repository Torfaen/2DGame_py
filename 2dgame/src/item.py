import pygame


#一个类对象，对应一个道具，道具生成在地图上，道具被玩家捡起后，道具效果生效，道具消失
class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height,name,effect):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        #道具名称，道具效果
        self.name = name
        self.effct=effect
        #道具生成xy坐标
        self.rect.x = x
        self.rect.y = y
        self.alive = True
        

    def effect(self):
        #道具效果，根据名字做判断
        if self.name == "speed_up":
            player.speed += 1
        elif self.name == "bomb_count_up":
            player.bomb_count += 1
        elif self.name == "bomb_power_up":
            player.bomb_power += 1


    def draw(self, window):
        window.blit(self.image, (self.rect.x, self.rect.y))


    def update(self):
        pass

    def get_rect(self):
        return self.rect

    def get_image(self):
        return self.image