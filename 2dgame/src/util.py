import pygame
import os


def load_sprites():
    # 加载所有帧
    frames = []
    for i in range(1, 9):  # 假设文件名为frame_1.png到frame_8.png
        frame_path = f"assets/sprites/player/idle/frame_{i}.png"
        frame = pygame.image.load(frame_path)
        frames.append(frame)