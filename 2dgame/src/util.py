import pygame
import os

from pygame.examples.sprite_texture import sprite
from config_loader import load_config
config_sprite=load_config("config_sprite.yaml")

def load_sprites():
    # 加载所有帧
    frames = []
    for i in range(1, 4):  # 假设文件名为frame_1.png到frame_3.png
        os.path.join("..", "assets", "sprites", "player")
        frame_path = os.path.join("..", "assets", "sprites", "player",f"manbo_sprite_{i}.png")
        frame = pygame.image.load(frame_path)
        frames.append(frame)

def get_sprite(path,tile_size,rows,cols,scale):
    #为了方便，直接返回二维数组
    sheet = pygame.image.load(os.path.join(path))
    sprites=[]
    for r in range(rows):
        row=[]
        for c in range(cols):
            surface = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA, 32)
            rect = pygame.Rect(c*tile_size, r*tile_size, tile_size, tile_size)
            surface.blit(sheet, (0, 0), rect)
            
            if scale != 1:
                width=int(surface.get_width() * scale)
                height=int(surface.get_height() * scale)
                surface=pygame.transform.scale(surface, (width, height))
            row.append(surface)
        sprites.append(row)
    return sprites


def load_sprite_path(sprite_name):
    path="assets/sprites/player/idle"
    return path

def load_map():
    pass
#---------------------测试区--------------------------------------------------------------------
def main():
    sprite_name="manbo"
    sprite_info=config_sprite["sprites"][f"{sprite_name}"]
    #sprite_name: manbo_sprite
    #路径
    path=sprite_info["path"]
    #sprite尺寸大小，一般为32x32
    tile_size=sprite_info["tile_size"]
    #sprite行数
    rows=sprite_info["rows"]
    #sprite列数
    cols=sprite_info["cols"]
    #sprite缩放比例
    scale=sprite_info["scale"]
    #sprite帧数
    frames=sprite_info["frames"]
    #sprite方向映射，如idle: { row: 0, cols: [0, 1, 2] }，表示idle方向的sprite在第0行，第0、1、2列
    mapping=sprite_info["mapping"]
    #获取所有需要的精灵图sprites
    #sprites=get_sprite(path,tile_size,rows,cols,scale)

    print(mapping.keys())
        

if __name__ == "__main__":
    main()

#---------------------测试区--------------------------------------------------------------------