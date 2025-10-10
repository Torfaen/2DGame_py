import os
from os import listdir
import pygame

from os.path import isfile,join
def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

#贴图处理逻辑
def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base_path, "assets", dir1, dir2)
    images=[f for f in listdir(path) if isfile(join(path, f))]
    all_sprites={}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites=[]
        for i in range(sprite_sheet.get_width()//width):
            surface = pygame.Surface((width, height),pygame.SRCALPHA,32)
            #创建一个surface,用来保存第i个图片
            rect=pygame.Rect(i*width,0,width,height)
            surface.blit(sprite_sheet, (0,0), rect)
            #剥离出所有帧
            sprites.append(pygame.transform.scale2x( surface))

            if direction:
                all_sprites[image.replace(".png", "") + "_right"] = sprites
                all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
            else :#无需反转处理的贴图，如蜡烛，树木
                all_sprites[image.replace(".png", "")] = sprites
    return all_sprites