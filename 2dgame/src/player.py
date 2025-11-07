import pygame
import os
from bomb import Bomb
from config_loader import load_config
from collections import deque
OFFSET_X = 24
OFFSET_Y = 56

config=load_config("config.yaml")
config_sprite=load_config("config_sprite.yaml")
config_player=load_config("config_player.yaml")

FPS=config["windows"]["fps"]
TILE_SIZE=config["windows"]["tile_size"]

class Player(pygame.sprite.Sprite):

    def __init__(self, id, x, y, controls, color,sprite_name,speed,speed_max,bombs_count,bombs_max,bomb_power,bomb_power_max, game_mode="ONE_LIFE"):
        super().__init__()  # 调用父类初始化
        self.images = {"left":[],"right":[],"up":[],"down":[]}
        self.id = id

        #控制键位
        self.controls = controls
        self.DIRECTION_KEYS = ("left", "right", "up", "down")
        self.keys_queue=deque()
        # 贴图相关
        # 玩家贴图
        # 临时填充颜色，后续版本改为传参
        self.color = color
        self.image = pygame.Surface((54, 61)) 
        self.image.fill(color) 
        self.rect = self.image.get_rect()
        self.height = config_sprite['sprites'][sprite_name]['height']
        self.width = config_sprite['sprites'][sprite_name]['width']
        #flg,显示玩家是几p
        self.id_flg = None
        self.id_flg_rect = None
        self.flg_width = config_player[f'player{self.id}']['flg_width']
        self.flg_height = config_player[f'player{self.id}']['flg_height']
        #出生点
        self.rect.x = x
        self.rect.y = y

        # 角色模型
        self.sprite_name=sprite_name
        self.frameIndex=0
        self.player_frame_counter = 0
        # 每15帧换一次贴图（60 FPS 下约 4 次/秒）
        self.ANIMATION_DELAY = 10
        # 动画库
        self.direction="down"
        self.frameMax = config_sprite['sprites'][sprite_name]['frames']
        self.image_shadow = None

        # 核心属性,道具改变
        self.speed = speed
        self.speed_max = speed_max
        # 移动相关
        # 速度x,y分量
        self.dx=0
        self.dy=0
        self.moved= False


        self.bombs_count = bombs_count
        self.bombs_max = bombs_max
        self.hit_box=None
        #泡泡冷却
        self.bomb_cooldown = 0
        # 0.2 秒冷却，60 FPS * 0.2 = 12 帧
        self.bomb_cooldown_max = FPS*0.25
        # 泡泡列表
        self.bombs_active = []
        self.cooldown = 0
        self.bombs_active = []

        self.bomb_power = bomb_power
        self.bomb_power_max = bomb_power_max

        self.status = "free"
        self.alive = True

        # 游戏模式
        self.game_mode = game_mode  # "POINT" 或 "ONE_LIFE"
        self.invincible_frames = 0  # 无敌帧数

        # 锚点坐标，用于判定在哪个格子

        self.feet_x = x + OFFSET_X
        self.feet_y = y + OFFSET_Y
        # 阴影矩形碰撞框
        self.feet_rect = pygame.Rect(0, 0, 5, 5)
        self.feet_rect.center = (self.feet_x, self.feet_y)
        #加载阴影贴图
        # 阴影贴图加载
        self._load_sprite()
        self._load_sprite_shadow()
        self._load_sprite_id_flg()
    def _load_sprite_shadow(self):
        try:
            shadow_path = os.path.join("..", "assets", "sprites", "player", "shadow.png")
            self.image_shadow = pygame.image.load(shadow_path)
            # self.image_shadow = pygame.transform.scale(self.image_shadow, (50, 20))  # 按需缩放
        except (pygame.error, FileNotFoundError) as e:
            print(f"警告：无法加载阴影图片 ({e})")
            self.image_shadow = None
    def _load_sprite_id_flg(self):
        try:
            id_flg_path = config_player[f'player{self.id}']['id_flg_path']
            self.id_flg = pygame.image.load(id_flg_path).convert_alpha()
            self.id_flg_rect = self.id_flg.get_rect()

        except (pygame.error, FileNotFoundError) as e:
            print(f"警告：无法加载id_flg图片 ({e})")
            self.id_flg = None

    def _load_sprite(self):
        # 加载玩家贴图,后续版本改为传参形式选角色
        sprite_name=self.sprite_name
        images={}
        try:
            base_path = os.path.join("..", "assets", "sprites", "player", sprite_name)
            for direction in self.images.keys():
                if os.path.exists(base_path):
                    frames=[]
                    for frameIndex in range(self.frameMax):
                        image_path = os.path.join(base_path, f"{direction}_{frameIndex}.png")
                        img=pygame.image.load(image_path).convert_alpha()
                        frames.append(img)
                    images[direction]=frames
                else:
                    print(f"警告：找不到图片 {base_path}")
            self.images = images

        except pygame.error as e:
            print(f"无法加载玩家图片: {e}")


    def _get_feetgrid_position(self):
        # 根据玩家锚点，获取当前格子坐标，向下取整
        # 例子：只要grid_x坐标在1-2内，那么grid_x则取1，以便绘制整个格子
        grid_x = int(self.feet_x // TILE_SIZE)
        grid_y = int(self.feet_y // TILE_SIZE)

        return grid_x, grid_y

    
    def update(self):
        """更新玩家内部状态（每帧调用）"""
        if not self.alive:
            self.die()
        self._update_player_bomb_cooldown()
        self._update_player_hitbox()
        self._update_direction()
        self._update_velocity()
        self._update_player_id_flg()
        self._update_frameIndex()
        self._update_image()


    def _update_player_id_flg(self):
        self.id_flg_rect.center = (self.feet_x, self.feet_y)
    def _update_player_hitbox(self):
        # 更新玩家碰撞框
        grid_x, grid_y = self._get_feetgrid_position()
        x=grid_x * TILE_SIZE
        y=grid_y * TILE_SIZE
        self.hit_box = pygame.Rect(x,
        y,TILE_SIZE, TILE_SIZE)
    
    def update_keys_queue(self,event):
        for key in self.DIRECTION_KEYS:
            #按下方向键
            if event.key == self.controls[key]:
                #按住方向键，加入队列
                if event.type == pygame.KEYDOWN and key not in self.keys_queue:
                    self.keys_queue.append(key)
                #松开方向键，移除队列
                elif event.type == pygame.KEYUP and key in self.keys_queue:
                    self.keys_queue.remove(key)
                #加break，没按的不判断，只判断按下的
                break
    def update_position(self,collision_rects):
        # 记录移动前坐标
            old_x, old_y = self.rect.x, self.rect.y
            old_feet_x, old_feet_y = self.feet_x, self.feet_y
            # 模型坐标
            self.rect.x+=self.dx
            self.rect.y+=self.dy
            # 锚点坐标
            self.feet_x+=self.dx
            self.feet_y+=self.dy
            # 同步 feet_rect 位置
            self.feet_rect.center = (self.feet_x, self.feet_y)
            if self.moved:
                for rect in collision_rects:
                    if self.if_in_collision(rect, old_feet_x, old_feet_y):
                        self.revert_move(old_x, old_y, old_feet_x, old_feet_y)
                        break
    def _update_frameIndex(self):
        if self.moved:
            self.player_frame_counter += 1
            if self.player_frame_counter >= self.ANIMATION_DELAY:
                self.player_frame_counter = 0
                self.frameIndex+=1
                if self.frameIndex >= self.frameMax:
                    self.frameIndex = 0

    def _update_image(self):
        if self.moved:
            self.image = self.images[self.direction][self.frameIndex]
        else:
            self.frameIndex=1
            self.image = self.images[self.direction][1]

    def die(self):
        self.kill()
        print(f"玩家{self.id}被炸死了")

    def hit_by_bomb(self, gamemode):
        # 或使用实际图像
        if gamemode == config["game"]["modes_allowed"][1]:
            self.image = pygame.Surface((54, 61))  
            # 临时填充白色
            self.image.fill((255, 0, 0))  
            self.alive = False
            self.status = "dead"
            self.die()

    def _update_player_bomb_cooldown(self):
        if self.bomb_cooldown > 0:
            self.bomb_cooldown -= 1

    #
    def _update_direction(self):
        if self.keys_queue:
            direction = self.keys_queue[-1]
        else:
            self.moved = False
            return
        if direction == "left":
            self.moved = True
            self.direction = "left"
        elif direction == "right":
            self.moved = True
            self.direction = "right"
        elif direction == "up":
            self.moved=True
            self.direction = "up"
        elif direction == "down":
            self.moved=True
            self.direction = "down"
        else:
            self.moved=False
    #更新速度，根据方向队列，更新速度
    def _update_velocity(self):
        self.dx=0
        self.dy=0
        if self.moved==True:
            if self.direction == "left":
                self.dx=-self.speed
                self.dy=0
            elif self.direction == "right":
                self.dx=self.speed
                self.dy=0
            elif self.direction == "up":
                self.dx=0
                self.dy=-self.speed
            elif self.direction == "down":
                self.dx=0
                self.dy=self.speed
        else :
            self.dx=0
            self.dy=0

   
    def if_in_collision(self,rect, old_feet_x, old_feet_y):
        # 检查玩家之前是否在障碍内
        old_feet_rect = pygame.Rect(0, 0, 5, 5)
        old_feet_rect.center = (old_feet_x, old_feet_y)
        if old_feet_rect.colliderect(rect):
            # 玩家之前在障碍内，可以自由移动（包括出去）
            return False
        
        # 玩家之前在障碍外，检查当前位置是否要进入障碍
        if self.feet_rect.colliderect(rect):
            # 玩家要进入障碍，阻止移动
            return True
        
        # 玩家既不在障碍内，也不进入障碍，可以移动
        return False


    def revert_move(self,old_x,old_y,old_feet_x,old_feet_y):
        #遇到障碍，移动回滚
         self.rect.x, self.rect.y = old_x, old_y
         self.feet_x, self.feet_y = old_feet_x, old_feet_y
         self.feet_rect.center = (self.feet_x, self.feet_y)

    def draw(self, window):
        #先渲染阴影
        if self.image_shadow:
            # 阴影绘制在脚下，以锚点为中心
            shadow_rect = self.image_shadow.get_rect()  # 获取阴影图片的rect
            shadow_rect.center = (self.feet_x, self.feet_y)  # 设置中心点在锚点
            window.blit(self.image_shadow, shadow_rect.topleft)  # 使用左上角坐标绘制
        # 渲染人物，使人物踩在影子上
        if self.images:
            y_fix=OFFSET_Y-self.height
            window.blit(self.image, (self.rect.x, self.rect.y + y_fix))
        else:
            # 没有贴图，绘制一个矩形代替角色
            pygame.draw.rect(window, self.color, (self.rect.x, self.rect.y, 50, 50))
        
    def draw_id_flg(self, window):
        if self.id_flg:
            x=self.feet_x - self.flg_width/2
            y=self.feet_y - OFFSET_Y - self.flg_height/2
            window.blit(self.id_flg, (x, y))

    def draw_debug_rect(self, window,DEBUG_MODE):
        if DEBUG_MODE:
            #人物贴图框
#           pygame.draw.rect(window, (255, 0, 0), (self.rect.x, self.rect.y, self.width, self.height), 1)
            # 角色hitbox框
            pygame.draw.rect(window, (0, 255, 0), self.hit_box, 1)
            # 角色hitbox锚点
            pygame.draw.circle(window, (0, 255, 0), (self.feet_x, self.feet_y), 5)
            # 阴影框
            #pygame.draw.rect(window, (0, 255, 0), self.feet_rect, 1)
    
    #修改属性接口，更新速度，炸弹数量，炸弹威力
    def update_speed(self,effect_value):
        self.speed = min(self.speed + effect_value, self.speed_max)

    def update_bombs_count(self,effect_value):
        self.bombs_count = min(self.bombs_count + effect_value, self.bombs_max)

    def update_bomb_power(self,effect_value):
        self.bomb_power = min(self.bomb_power + effect_value, self.bomb_power_max)
        
    # 道具类型控制器，根据道具类型，更新玩家属性
    def update_item_effect(self,dict_effect):
        # 增加属性 一点值系列道具
        if dict_effect["type"] == "speed":
            self.update_speed(dict_effect["value"]) 

        elif dict_effect["type"] == "bomb_count":
            self.update_bombs_count(dict_effect["value"])   

        elif dict_effect["type"] == "bomb_power":
            self.update_bomb_power(dict_effect["value"])

        # 增加属性 最大值系列道具
        elif dict_effect["type"] == "speed_max":
            self.update_speed(dict_effect["value"])

        elif dict_effect["type"] == "bomb_count_max":
            self.update_bombs_count(dict_effect["value"])

        elif dict_effect["type"] == "bomb_power_max":
            self.update_bomb_power(dict_effect["value"])