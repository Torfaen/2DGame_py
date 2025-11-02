import random

import pygame
from config_loader import load_config
from util import get_sprite

#生成方式：炸掉物块，概率生成
#一个类对象，对应一个道具，道具生成在地图上，道具被玩家捡起后，道具效果生效，道具消失
config_items = load_config("config_items.yaml")
config = load_config("config.yaml")
TILE_SIZE = config["windows"]["tile_size"]
class Item(pygame.sprite.Sprite):
    items=config_items["items"]
    items_keys = list(items.keys())
    sprites={}
    for item_key in items_keys:
        item=items[item_key]
        name=item["name"]
        sprite_path=item["sprite_path"]
        width=item["width"]
        height=item["height"]
        rows=item["rows"]
        cols=item["cols"]
        # 存储所有序列帧贴图的字典，key为道具名称，value为序列帧贴图列表
        sprites[name]=get_sprite(sprite_path,width,height,rows,cols,scale=1)
    
    def __init__(self, x, y, width, height,name,effect_type,effect_value,path):
        super().__init__()
        self.rect = pygame.Rect(x, y, width , height)
        self.hit_box = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.width = width
        self.height = height
        #道具名称，道具效果
        self.name = name
        #道具贴图索引
        self.sprite_index = 0
        #动画相关
        self.frame_counter = 0
        self.ANIMATION_DELAY = 20  # 每10帧切换一次动画
        #更新道具贴图（必须在 self.name 设置之后）
        self.image = self.load_sprite(self.sprite_index)
        # "speed", "bomb_count", "bomb_power"
        self.effect_type = effect_type  
         # 增加值，如 1
        self.effect_value = effect_value 
        # 道具图片路径
        self.path = path
        # 道具生成xy坐标
        self.rect.x = x
        self.rect.y = y
        self.alive = True

    @classmethod
    def create_random(cls,rect_x,rect_y):
        item_name = random.choice(cls.items_keys)
        item_config = cls.items[item_name]
        item = cls(x=rect_x, y=rect_y,name=item_config["name"], 
                    width=item_config["width"], height=item_config["height"],
                    effect_type=item_config["effect_type"], effect_value=item_config["effect_value"], 
                    path=item_config["sprite_path"])
        return item


    def load_sprite(self,sprite_index):
        try:
            image=Item.sprites[self.name][0][sprite_index]
        except Exception as e:
            print(f"加载道具贴图失败: {e}")
            image=pygame.Surface((self.width, self.height), pygame.SRCALPHA, 32)
            image.fill((0,255,0))
        return image

    def _update_sprite(self):
        # 管理贴图循环播放
        self.frame_counter += 1
        if self.frame_counter >= self.ANIMATION_DELAY:
            self.frame_counter = 0
            self.sprite_index = (self.sprite_index + 1) % len(Item.sprites[self.name][0])
            self.image = self.load_sprite(self.sprite_index)

    def _update_alive(self):
        if not self.alive:
            self.kill()
            
    def draw(self, window):
        y_offset=self.rect.y+(TILE_SIZE-self.height)
        window.blit(self.image, (self.rect.x, y_offset))

    def draw_debug_rect(self, window,DEBUG_MODE):
        if DEBUG_MODE:
            #道具贴图框
            pygame.draw.rect(window, (0, 255, 0), self.rect, 1)

    def update(self):
        self._update_sprite()
        self._update_alive()


    def get_rect(self):
        return self.rect

    def get_image(self):
        return self.image

    def get_effect(self):
        dict_effect={"type":self.effect_type,"value":self.effect_value}
        return dict_effect

    