from re import S
import pygame
import os

from macholib.ptypes import sizeof

from config_loader import load_config, dict_controls
config=load_config()
TILE_SIZE=config["windows"]["tile_size"]
FPS=config["windows"]["fps"]
#爆炸区域类，一个类对象对应一个炸弹爆炸产生的爆炸区域，main函数创建一个group存储所有爆炸区域
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, power, map_obj=None):
        super().__init__()
        # 爆炸区域信息列表
        # 每个元素：{"pos": (gx, gy), "direction": "up/down/left/right/center", "is_end": bool}
        self.grids_info = []
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.power = power

        self.map_obj = map_obj

        # 爆炸持续时间,t/FPS=0.5s
        self.explosion_timer = 30
        self.explosion_handled = False
        
        # 计算爆炸范围（格子坐标）
        #   返回
        self._calculate_explosion_area(map_obj)
        
        # 加载爆炸贴图
        self.image_mid= {
            "center":self._load_explosion_sprite("center"),
            "right":self._load_explosion_sprite("right"),
            "left":self._load_explosion_sprite("left"),
            "up":self._load_explosion_sprite("up"),
            "down":self._load_explosion_sprite("down"),
            }
        self.image_end= {
            "center":self._load_explosion_sprite("center",True),
            "right":self._load_explosion_sprite("right",True),
            "left":self._load_explosion_sprite("left",True),
            "up":self._load_explosion_sprite("up",True),
            "down":self._load_explosion_sprite("down",True),
            }
        
    def contains(self, grid_x, grid_y):
        """检查指定格子是否在爆炸范围内"""
        return any(grid["pos"] == (grid_x, grid_y) for grid in self.grids_info)

    def update(self):
        self.explosion_timer-=1
        self._update_image()
        if self.explosion_timer<=0:
            self.kill()


    def destroy_blocks_in_explosion(self):
        # 转换为格子坐标
        bomb_grid_x = self.rect.x // TILE_SIZE
        bomb_grid_y = self.rect.y // TILE_SIZE
        
        #上下左右
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]  
        #四向遍历
        for dx, dy in directions:
            for i in range(1, self.power + 1):
                check_grid_x = bomb_grid_x + dx * i
                check_grid_y = bomb_grid_y + dy * i                
                # 边界检查，地图左上角为(0,0),右下角为(len(map_obj.barrier_map[0])-1,len(map_obj.barrier_map)-1)
                # 若x<0则超左边界，x大于len(map_obj.barrier_map[0])-1则超右边界，
                # y<0则超上边界，y大于len(map_obj.barrier_map)-1则超下边界
                if (check_grid_x < 0 or check_grid_x >= len(self.map_obj.barrier_map[0]) or 
                    check_grid_y < 0 or check_grid_y >= len(self.map_obj.barrier_map)):
                    # 超出边界，跳出当前方向循环
                    break  
                # 障碍物检查
                if self.map_obj.barrier_map[check_grid_y][check_grid_x] != "empty":
                    # 遇到障碍物，记录摧毁的方块
                    #self.destroyed_blocks.append((check_grid_x, check_grid_y))
                    # 分离计算与摧毁，不然会造成贯穿摧毁
                    self.map_obj.remove_barrier(check_grid_x, check_grid_y)
                    self.map_obj.remove_collision(check_grid_x, check_grid_y)
                    break
    

    def _update_image(self):
        for grid_info in self.grids_info:
            grid_x=grid_info["pos"][0]
            grid_y=grid_info["pos"][1]
            direction=grid_info["direction"]
            is_end=grid_info["is_end"]
            if not is_end:
                self.image_mid[direction]=self._load_explosion_sprite(direction,is_end)
            else:
                self.image_end[direction]=self._load_explosion_sprite(direction,is_end)

    
    def draw(self, window):
        for info in self.grids_info:
            grid_x,grid_y=info["pos"]
            direction=info["direction"]
            is_end=info["is_end"]
            if not is_end:
                window.blit(self.image_mid[direction], (grid_x * TILE_SIZE, grid_y * TILE_SIZE, 32, 32 ))
            else:
                window.blit(self.image_end[direction], (grid_x * TILE_SIZE, grid_y * TILE_SIZE, 32, 32 ))

    def _calculate_explosion_area(self, map_obj):
        explosion_area = []
        # 转换为格子坐标
        bomb_grid_x = self.rect.x // TILE_SIZE
        bomb_grid_y = self.rect.y // TILE_SIZE
        
        self.grids_info.append({"pos":(bomb_grid_x, bomb_grid_y), "direction":"center", "is_end":False})
        #上下左右
        directions = [(0, -1,"up"), (0, 1,"down"), (-1, 0,"left"), (1, 0,"right")]  
        #四向遍历
        for dx, dy ,direction in directions:
            for i in range(1, self.power + 1):
                check_grid_x = bomb_grid_x + dx * i
                check_grid_y = bomb_grid_y + dy * i
                # 边界检查，地图左上角为(0,0),右下角为(len(map_obj.barrier_map[0])-1,len(map_obj.barrier_map)-1)
                # 若x<0则超左边界，x大于len(map_obj.barrier_map[0])-1则超右边界，
                # y<0则超上边界，y大于len(map_obj.barrier_map)-1则超下边界
                if (check_grid_x < 0 or check_grid_x >= len(map_obj.barrier_map[0]) or
                    check_grid_y < 0 or check_grid_y >= len(map_obj.barrier_map)):
                    # 超出边界，跳出当前方向循环
                    break  
                # 障碍物检查
                if map_obj.barrier_map[check_grid_y][check_grid_x] != "empty":
                    break
                #爆炸区域信息添加
                if i == self.power:
                    self.grids_info.append({"pos":(check_grid_x, check_grid_y), "direction":direction, "is_end":True})
                else:
                    self.grids_info.append({"pos":(check_grid_x, check_grid_y), "direction":direction, "is_end":False})

    def _load_explosion_sprite(self , direction , is_end = False):
        size=(32,32)
        # 判断中心
        if direction == "center":
            path=os.path.join("..", "assets", "sprites", "bomb", "center.png")
            image=pygame.image.load(path)
            image = pygame.transform.scale(image,(32,32))
            return image
        # 判断四周爆炸
        if is_end:
            path=os.path.join("..", "assets", "sprites", "bomb", "explosion_1.png")
        else:
            path=os.path.join("..", "assets", "sprites", "bomb", "explosion_0.png")
        #加载泡泡贴图
        try:
            image = pygame.image.load(path)
            if direction == "right":
                pass
            elif direction == "left":
                image = pygame.transform.flip(image, True, False)
            elif direction == "up":
                image = pygame.transform.rotate(image, 90)
            elif direction == "down":
                image = pygame.transform.rotate(image, -90)

            image = pygame.transform.scale(image,(32,32))
            return image

        except (pygame.error, FileNotFoundError) as e:
            # 临时方块贴图
            surface = pygame.Surface(size, pygame.SRCALPHA)
            #pygame.draw.rect(self.image_bomb, (173, 216, 230), (self.rect.x, self.rect.y, 32, 32))
            pygame.draw.rect(surface, (173, 216, 230), surface.get_rect())
            print(f"警告：无法加载爆炸图片 ({e})")
            return surface

