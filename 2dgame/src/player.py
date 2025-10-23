import pygame
import os

from pygame.examples.grid import TILE_SIZE

from bomb import Bomb
FPS=60
class Player(pygame.sprite.Sprite):

    def __init__(self, id, x, y, controls, color, game_mode="ONE_LIFE"):
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
        self.tile_size = 32

        # 核心属性
        self.speed = 4
        self.status = "free"
        self.alive = True
        
        # 游戏模式
        self.game_mode = game_mode  # "POINT" 或 "ONE_LIFE"
        self.invincible_frames = 0  # 无敌帧数
        
        # 锚点坐标，用于画阴影碰撞框

        self.feet_x = x+14
        self.feet_y = y+50
        # 阴影矩形碰撞框
        self.feet_rect = pygame.Rect(self.feet_x, self.feet_y, 24, 10)

        # 泡泡属性
        self.max_bombs = 100
        self.bomb_power = 6
        #泡泡冷却
        self.bomb_cooldown = 0
        # 0.2 秒冷却，60 FPS * 0.2 = 12 帧
        self.bomb_cooldown_max = FPS*0.25
        # 泡泡列表
        self.bombs_active = []
        self.invincible_timer = 0
        self.score = 0
        self.powerups = {}
        self.cooldown = 0
        self.bombs_active = []

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
            base_path = os.path.join("..", "assets", "sprites", "player", "player2_sprite")
            for direction in self.images.keys():
                image_path = os.path.join(base_path, f"{direction}.png")
                if os.path.exists(image_path):
                    self.images[direction] = pygame.image.load(image_path)
                    self.images[direction] = pygame.transform.scale(self.images[direction], (54, 61))
                else:
                    print(f"警告：找不到图片 {image_path}")
        except pygame.error as e:
            print(f"无法加载玩家图片: {e}")

    def update(self):
        """更新玩家内部状态（每帧调用）"""
        if not self.alive:
            self._die()
        self._update_player_bomb_cooldown()

    def ifInExplosion(self, explosion_rects):
        if explosion_rects is None:
            return False
        for rect in explosion_rects:
            if self.feet_rect.colliderect(rect):
                return True
        return False

    def _die(self):
    
        self.kill()
        print(f"玩家{self.id}被炸死了")

    def hit_by_bomb(self, gamemode):
        # 或使用实际图像
        if gamemode == "ONE_LIFE":
            self.image = pygame.Surface((54, 61))  
            # 临时填充白色
            self.image.fill((255, 0, 0))  
            self.alive = False
            self.status = "dead"
            self._die()


    def _update_player_bomb_cooldown(self):
        if self.bomb_cooldown > 0:
            self.bomb_cooldown -= 1


    def handle_bomb_group(self, bombs_group,map_obj):
        # 检查当前想激活的泡泡是否合法，移除已经爆炸的泡泡
        self.bombs_active = [b for b in self.bombs_active if not b.exploded]
        if len(self.bombs_active) >= self.max_bombs:
            return None
        # round固定泡泡坐标在格子中心
        x = round(self.feet_rect.centerx // self.tile_size) * self.tile_size
        y = round(self.feet_rect.centery // self.tile_size) * self.tile_size

        for bomb in self.bombs_active:
            if bomb.rect.x == x and bomb.rect.y == y:
                return None

        bomb_new=Bomb(x,y,self.bomb_power,map_obj=map_obj)
        self.bombs_active.append(bomb_new)
        #合法的泡泡添加进容器
        bombs_group.add(bomb_new)
        #放下泡泡，开始冷却
        self.bomb_cooldown = self.bomb_cooldown_max
        return bomb_new

    def place_bomb(self, bombs_group,map_obj):
        """按键长按检测版：按下就尝试放置炸弹"""
        keys = pygame.key.get_pressed()
        if keys[self.controls["shift"]] and self.bomb_cooldown <= 0:
            self.handle_bomb_group(bombs_group,map_obj)


    def move(self, dx, dy,collision_rects):
        # 记录坐标
        old_x, old_y = self.rect.x, self.rect.y
        old_feet_x, old_feet_y = self.feet_x, self.feet_y
        moved= False
        key = pygame.key.get_pressed()

        if key[self.controls["left"]]:
            self.rect.x -= self.speed
            self.feet_x-=self.speed
            self.direction = "left"
            moved = True

        elif key[self.controls["right"]]:
            self.rect.x += self.speed
            self.feet_x+=self.speed
            self.direction = "right"
            moved = True

        elif key[self.controls["up"]]:
            self.rect.y -= self.speed
            self.feet_y-=self.speed
            self.direction = "up"
            moved = True

        elif key[self.controls["down"]]:
            self.rect.y += self.speed
            self.feet_y+=self.speed
            self.direction = "down"
            moved = True

        # 同步 feet_rect 位置
        self.feet_rect.topleft = (self.feet_x, self.feet_y)
        if moved:
            for rect in collision_rects:
                #老的障碍判断逻辑，弃用
                #if self.feet_rect.colliderect(rect):
                if self._if_in_collision(rect, old_feet_x, old_feet_y):
                    self._revert_move(old_x, old_y, old_feet_x, old_feet_y)
                    break

   
    def _if_in_collision(self,rect, old_feet_x, old_feet_y):
        # 检查玩家之前是否在障碍内
        old_feet_rect = pygame.Rect(old_feet_x, old_feet_y, 24, 10)
        if old_feet_rect.colliderect(rect):
            # 玩家之前在障碍内，可以自由移动（包括出去）
            return False
        
        # 玩家之前在障碍外，检查当前位置是否要进入障碍
        if self.feet_rect.colliderect(rect):
            # 玩家要进入障碍，阻止移动
            return True
        
        # 玩家既不在障碍内，也不进入障碍，可以移动
        return False


    def _revert_move(self,old_x,old_y,old_feet_x,old_feet_y):
        #遇到障碍，移动回滚
         self.rect.x, self.rect.y = old_x, old_y
         self.feet_x, self.feet_y = old_feet_x, old_feet_y
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
            #人物贴图框
#            pygame.draw.rect(window, (255, 0, 0), (self.rect.x, self.rect.y, 54, 61), 1)
            # 阴影框
            pygame.draw.rect(window, (0, 255, 0), self.feet_rect, 1)
    

    def load_sprite(self, width, height):
        # 此方法已废弃，无需使用
        pass
