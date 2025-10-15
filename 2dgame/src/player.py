import pygame
import os


class Player(pygame.sprite.Sprite):
    def __init__(self, id, x, y, controls, color):
        super().__init__()  # 调用父类初始化
        self.id = id
        self.image = pygame.Surface((54, 61))  # 或使用实际图像
        self.image.fill(color)  # 临时填充颜色
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.controls = controls
        self.color = color
        self.direction = "down"

        # 核心属性
        self.speed = 4
        self.max_bombs = 1
        self.bomb_power = 1
        self.status = "free"
        self.alive = True
        # 锚点坐标，用于画阴影碰撞框

        self.feet_x = x+11
        self.feet_y = y+50
        # 阴影矩形碰撞框
        self.feet_rect = pygame.Rect(self.feet_x, self.feet_y, 30, 10)

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

        #加载阴影贴图
        # 阴影贴图加载
        try:
            shadow_path = os.path.join("..", "assets", "sprites", "background", "map_base", "shadow.png")
            self.image_shadow = pygame.image.load(shadow_path)
            #self.image_shadow = pygame.transform.scale(self.image_shadow, (50, 20))  # 按需缩放
        except (pygame.error, FileNotFoundError) as e:
            print(f"警告：无法加载阴影图片 ({e})")
            self.image_shadow = None

        #加载玩家贴图,后续版本改为传参形式选角色
        try:
            base_path = os.path.join("..", "assets", "sprites", "player", "player1_sprite")
            for direction in self.images.keys():
                image_path = os.path.join(base_path, f"{direction}.png")
                if os.path.exists(image_path):
                    self.images[direction] = pygame.image.load(image_path)
                    self.images[direction] = pygame.transform.scale(self.images[direction], (54, 61))
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
            self.rect.x -= self.speed
            self.feet_x-=self.speed
            self.direction = "left"

        elif key[self.controls["right"]]:
            self.rect.x += self.speed
            self.feet_x+=self.speed
            self.direction = "right"
        elif key[self.controls["up"]]:
            self.rect.y -= self.speed
            self.feet_y-=self.speed
            self.direction = "up"
        elif key[self.controls["down"]]:
            self.rect.y += self.speed
            self.feet_y+=self.speed
            self.direction = "down"
        # 同步 feet_rect 位置
        self.feet_rect.topleft = (self.feet_x, self.feet_y)

    def draw(self, window):
        #先渲染阴影
        if self.image_shadow:
            # 阴影绘制在脚下
            shadow_x = self.feet_x
            shadow_y = self.feet_y
            window.blit(self.image_shadow, (shadow_x, shadow_y))
        # 渲染人物，使人物踩在影子上
        if self.images and self.direction in self.images and self.images[self.direction]:
            window.blit(self.images[self.direction], (self.rect.x, self.rect.y))
        else:
            # 没有贴图，绘制一个矩形代替角色
            pygame.draw.rect(window, self.color, (self.rect.x, self.rect.y, 50, 50))


    def draw_debug_rect(self, window,DEBUG_MODE):
        if DEBUG_MODE:
#            pygame.draw.rect(window, (255, 0, 0), (self.rect.x, self.rect.y, 54, 61), 1)
            pygame.draw.rect(window, (0, 255, 0), self.feet_rect, 1)


    def load_sprite(self, width, height):
        # 此方法已废弃，无需使用
        pass
