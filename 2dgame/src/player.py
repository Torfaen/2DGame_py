import pygame
import os


class Player():
    def __init__(self, id, x, y, controls, color):
        self.id = id
        self.x = x
        self.y = y
        self.controls = controls
        self.color = color
        self.direction = "down"

        # 核心属性
        self.speed = 4
        self.max_bombs = 1
        self.bomb_power = 1
        self.status = "free"
        self.alive = True
        self.feet_y = self.y + 64  # 锚点y坐标

        # 扩展属性
        self.bombs_active = []
        self.invincible_timer = 0
        self.score = 0
        self.powerups = {}
        self.cooldown = 0

        # 加载各个方向的图像
        self.images = {
            "down": None,
            "up": None,
            "left": None,
            "right": None
        }

        try:
            base_path = os.path.join("..", "assets", "sprites", "player", "player1_sprite")
            for direction in self.images.keys():
                image_path = os.path.join(base_path, f"{direction}.png")
                if os.path.exists(image_path):
                    self.images[direction] = pygame.image.load(image_path)
                    #self.images[direction] = pygame.transform.scale(self.images[direction], (50, 50))
                else:
                    print(f"警告：找不到图片 {image_path}")
        except pygame.error as e:
            print(f"无法加载玩家图片: {e}")

        # 移除不需要的精灵图相关字段
        self.animation_timer = 0
        self.animation_speed = 10
        self.current_frame = 0
        self.frames = []  # 不再使用

    def move(self, dx, dy):
        key = pygame.key.get_pressed()
        if key[self.controls["left"]]:
            self.x -= self.speed
            self.direction = "left"
        elif key[self.controls["right"]]:
            self.x += self.speed
            self.direction = "right"
        elif key[self.controls["up"]]:
            self.y -= self.speed
            self.direction = "up"
        elif key[self.controls["down"]]:
            self.y += self.speed
            self.direction = "down"

    def draw(self, window):
        if self.images and self.direction in self.images and self.images[self.direction]:
            window.blit(self.images[self.direction], (self.x, self.y))
        else:
            pygame.draw.rect(window, self.color, (self.x, self.y, 50, 50))

    def load_sprite(self, width, height):
        # 此方法已废弃，无需使用
        pass
