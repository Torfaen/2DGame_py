import pygame
import os

from pygame.examples.sprite_texture import sprite


def load_sprites():
    # 加载所有帧
    frames = []
    for i in range(1, 4):  # 假设文件名为frame_1.png到frame_3.png
        os.path.join("..", "assets", "sprites", "player")
        frame_path = os.path.join("..", "assets", "sprites", "player",f"manbo_sprite_{i}.png")
        frame = pygame.image.load(frame_path)
        frames.append(frame)

def get_sprite(path):
    path = os.path.join("..", "assets", "sprites", "player","曼波与哈基米.png")
    sprite_sheet = pygame.image.load(os.path.join(path)).convert_alpha()
    tile_size = 32
    sprites=[]
    for x in range(0,3):
        for y in range(0,4):
            surface = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA, 32)
            rect = pygame.Rect(x, y, tile_size, tile_size)
            surface.blit(sprite_sheet, (0, 0), rect)

            sprites.append(pygame.transform.scale2x(surface))


def load_sprite_path(sprite_name):
    path="assets/sprites/player/idle"
    return path

def load_map():
    pass