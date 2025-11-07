import random

import pygame
from config_loader import load_config
from util import get_sprite
#生成方式：炸掉物块，概率生成
#一个类对象，对应一个道具，道具生成在地图上，道具被玩家捡起后，道具效果生效，道具消失
config_items = load_config("config_items.yaml")
config = load_config("config.yaml")
TILE_SIZE = config["windows"]["tile_size"]

class BaseItem(pygame.sprite.Sprite):

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
        anchor_x=item["anchor_x"]
        anchor_y=item["anchor_y"]
        # 存储所有序列帧贴图的字典，key为道具名称，value为序列帧贴图列表
        sprites[name]=get_sprite(sprite_path,width,height,rows,cols,scale=1)
        
    def __init__(self, x, y, config_item):
        super().__init__()
        self.hit_box = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.width = config_item["width"]
        self.height = config_item["height"]
        #道具名称，道具效果
        self.name = config_item["name"]
        #道具贴图索引
        self.sprite_index = 0
        #动画相关
        self.frame_counter = 0
        self.ANIMATION_DELAY = 20  # 每10帧切换一次动画
        #更新道具贴图（必须在 self.name 设置之后）
        self.image = self.load_sprite(self.sprite_index)
        # "speed", "bomb_count", "bomb_power"
        self.effect_type = config_item["effect_type"]  
         # 增加值，如 1
        self.effect_value = config_item["effect_value"]  
        # 道具图片路径
        self.path = config_item["sprite_path"]
        # 道具生成xy坐标
        self.rect = pygame.Rect(x, y-config_item["anchor_y"], self.width, self.height)
        self.rect.x = x
        self.rect.y = y
        self.anchor_x = config_item["anchor_x"]
        self.anchor_y = config_item["anchor_y"]

        self.alive = True
    @classmethod
    def create_random(cls,rect_x,rect_y):
        item_key = random.choice(cls.items_keys)
        item_class = ITEM_CLASS_MAP[item_key]
        item = item_class(x=rect_x, y=rect_y,config_item=config_items["items"][item_key])
        return item
    def load_sprite(self,sprite_index):
        try:
            image=BaseItem.sprites[self.name][0][sprite_index]
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
            self.sprite_index = (self.sprite_index + 1) % len(BaseItem.sprites[self.name][0])
            self.image = self.load_sprite(self.sprite_index)

    def _update_alive(self):
        if not self.alive:
            self.kill()
            
    def draw(self, window):
        window.blit(self.image, (self.rect.x, self.rect.y-self.anchor_y))

    def draw_debug_rect(self, window,DEBUG_MODE):
        if DEBUG_MODE:
            #道具hitbox框
            pygame.draw.rect(window, (0, 255, 0), self.hit_box, 1)

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
    def apply(self,player_obj):
        pass

class BombCountItem(BaseItem):
    def __init__(self, x, y,config_item):
        super().__init__(x, y,config_item)
    def apply(self,player_obj):
        player_obj.update_bombs_count(self.effect_value)

class BombPowerItem(BaseItem):
    def __init__(self, x, y,config_item):
        super().__init__(x, y,config_item)
    def apply(self,player_obj):
        player_obj.update_bomb_power(self.effect_value)

class SpeedItem(BaseItem):
    def __init__(self, x, y,config_item):
        super().__init__(x, y,config_item)
    def apply(self,player_obj):
        player_obj.update_speed(self.effect_value)

class SpeedMaxItem(BaseItem):
    def __init__(self, x, y,config_item):
        super().__init__(x, y,config_item)
    def apply(self,player_obj):
        player_obj.update_speed(self.effect_value)

ITEM_CLASS_MAP = {
    "bomb_count_up": BombCountItem,
    "bomb_power_up": BombPowerItem,
    "speed_up": SpeedItem,
    "speed_max": SpeedMaxItem,

}
