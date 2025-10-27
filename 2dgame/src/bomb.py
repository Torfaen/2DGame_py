import pygame
import os

TILE_SIZE=32
FPS=60
#爆炸区域类，一个类对象对应一个爆炸区域，main函数创建一个group存储所有爆炸区域
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, power):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill((255,0,0), (0,0,0))
        self.rect = self.image.get_rect()
        # 爆炸持续时间,t/FPS=0.5s
        self.explosion_timer = 30
        self.explosion_area=[]
        self.power = power
        self.alive= False
        self.alive_timer = 0

    def update(self,explosion_area):
        self.explosion_timer-=1
        if self.explosion_timer<=0:
            self.kill()

    def add(self,bomb,x,y):
        '''
        不需要去重检测，爆炸是可以叠加的
        if any(rect.x == x * TILE_SIZE and rect.y == y * TILE_SIZE
               for rect in self.explosion_area):
            return
        '''
        self.explosion_area.append(pygame.Rect(x , y , TILE_SIZE, TILE_SIZE))
    def remove(self,x,y):
        self.explosion_area.remove(pygame.Rect(x , y , TILE_SIZE, TILE_SIZE))

    def draw(self, window):
        for rect in self.explosion_area:
            try:
                window.blit(self.image, rect)
            except (pygame.error, FileNotFoundError) as e:
                # 临时方块贴图
                surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                # pygame.draw.rect(self.image_bomb, (173, 216, 230), (self.rect.x, self.rect.y, 32, 32))
                pygame.draw.rect(surface, (255, 0, 0), surface.get_rect())
                print(f"警告：无法加载爆炸贴图 ({e})")

    def _calculate_explosion_area(self, map_obj):
        explosion_area = []
        # 转换为格子坐标
        bomb_x = self.rect.x // TILE_SIZE
        bomb_y = self.rect.y // TILE_SIZE
        
        #上下左右
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]  
        #四向遍历
        for dx, dy in directions:
            for i in range(1, self.power + 1):
                check_x = bomb_x + dx * i
                check_y = bomb_y + dy * i                
                # 边界检查，地图左上角为(0,0),右下角为(len(map_obj.barrier_map[0])-1,len(map_obj.barrier_map)-1)
                # 若x<0则超左边界，x大于len(map_obj.barrier_map[0])-1则超右边界，
                # y<0则超上边界，y大于len(map_obj.barrier_map)-1则超下边界
                if (check_x < 0 or check_x >= len(map_obj.barrier_map[0]) or 
                    check_y < 0 or check_y >= len(map_obj.barrier_map)):
                    # 超出边界，跳出当前方向循环
                    break  
                # 障碍物检查
                if map_obj.barrier_map[check_y][check_x] != "empty":
                    # 遇到障碍物，停止该方向的爆炸
                    #self.destroyed_blocks.append((check_x, check_y))
                    #分离计算与摧毁，不然会造成贯穿摧毁
                    #map_obj.remove_barrier(check_x, check_y)
                    #map_obj.remove_collision(check_x, check_y)
                    #explosion_area.append((check_x, check_y))  # 障碍物位置也算在爆炸范围内
                    break
                #爆炸区域像素xy坐标以及rect
                self.explosion_area.append(pygame.Rect(check_x * TILE_SIZE, check_y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                #格子坐标
                explosion_area.append((check_x, check_y))
        print("爆炸范围：", explosion_area)
        return explosion_area


#泡泡类，一个类对应多个泡泡对象
class Bomb(pygame.sprite.Sprite):
    def __init__(self, x, y, power, color=(173, 216, 230),map_obj=None):
        #基础属性
        super().__init__()  # 调用父类初始化
        self.explosion_rect = []
        self.image = pygame.Surface((20, 20))  # 或使用实际图像
        self.image.fill(color)  # 临时填充颜色
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        #地图对象
        self.map_obj = map_obj
        # 炸弹放置时,创建阻挡
        if self.map_obj:
            self._generate_collision(x,y)
        #泡泡爆炸相关
        self.power = power
        self.timer = 0
        self.exploded = False
        #破坏的方块列表
        self.destroyed_blocks = []
        #爆炸波及的区域rect,一个泡泡对于一个爆炸区域，主函数创造一个group存储所有爆炸区域
        self.explosion_area = []
        #泡泡爆炸动画持续时间
        self.explosion_timer = 0
        # 是否已经处理过爆炸逻辑
        self.explosion_handled = False
        # 加载各个状态的图像
        self.images = {
            "center":None,
            "down": None,
            "up": None,
            "left": None,
            "right": None
        }
        #临时贴图
        bomb_path = os.path.join("..", "assets", "sprites", "bomb", "idle_0.png")
        self.image_bomb= self.load_bomb_sprite(bomb_path)
    # 放置时产生阻挡
    def _generate_collision(self,x,y):
        grid_x = x // TILE_SIZE
        grid_y = y // TILE_SIZE
        self.map_obj.generate_collision(grid_x,grid_y)
    
    # 爆炸时移除阻挡
    def _remove_collision(self,x,y):        
        grid_x = x // TILE_SIZE
        grid_y = y // TILE_SIZE
        self.map_obj.remove_collision(grid_x,grid_y)


        '''类内初始化贴图，已弃用
        #加载泡泡贴图
        try:
            shadow_path = os.path.join("..", "assets", "sprites", "bomb", "idle_0.png")
            self.image_bomb = pygame.image.load(shadow_path)
            #self.image_shadow = pygame.transform.scale(self.image_shadow, (50, 20))  # 按需缩放
        except (pygame.error, FileNotFoundError) as e:
            self.image_bomb = pygame.Surface((40, 40), pygame.SRCALPHA)
            #临时方块贴图
            #pygame.draw.rect(self.image_bomb, (173, 216, 230), (self.rect.x, self.rect.y, 32, 32))
            pygame.draw.circle(self.image_bomb, (173, 216, 230), (10, 10), 13)
            print(f"警告：无法加载泡泡图片 ({e})")
        '''
    def load_bomb_sprite(self,path,size=(32,32)):
        #加载泡泡贴图
        try:
            image = pygame.image.load(path)
            image = pygame.transform.scale(image,size)
            return image
        except (pygame.error, FileNotFoundError) as e:
            # 临时方块贴图
            surface = pygame.Surface(size, pygame.SRCALPHA)
            #pygame.draw.rect(self.image_bomb, (173, 216, 230), (self.rect.x, self.rect.y, 32, 32))
            pygame.draw.rect(surface, (173, 216, 230), surface.get_rect())
            print(f"警告：无法加载泡泡图片 ({e})")
            return surface

    def trigger_explosion(self):
        #连锁爆炸，直接设置爆炸状态为True
        self.exploded = True
        # 爆炸持续时间
        self.explosion_timer = 30 
        # 爆炸时移除阻挡

        self._remove_collision(self.rect.x,self.rect.y)
        print("触发爆炸")

    
    def get_explosion_area(self):
        explosion_area = []
        # 转换为格子坐标
        bomb_x = self.rect.x // TILE_SIZE
        bomb_y = self.rect.y // TILE_SIZE
        
        #上下左右
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]  
        #四向遍历
        for dx, dy in directions:
            for i in range(1, self.power + 1):
                check_x = bomb_x + dx * i
                check_y = bomb_y + dy * i                
                # 边界检查，地图左上角为(0,0),右下角为(len(map_obj.barrier_map[0])-1,len(map_obj.barrier_map)-1)
                # 若x<0则超左边界，x大于len(map_obj.barrier_map[0])-1则超右边界，
                # y<0则超上边界，y大于len(map_obj.barrier_map)-1则超下边界
                if (check_x < 0 or check_x >= len(self.map_obj.barrier_map[0]) or 
                    check_y < 0 or check_y >= len(self.map_obj.barrier_map)):
                    # 超出边界，跳出当前方向循环
                    break  
                # 障碍物检查
                if self.map_obj.barrier_map[check_y][check_x] != "empty":
                    # 遇到障碍物，停止该方向的爆炸
                    #self.destroyed_blocks.append((check_x, check_y))
                    #分离计算与摧毁，不然会造成贯穿摧毁
                    #map_obj.remove_barrier(check_x, check_y)
                    #map_obj.remove_collision(check_x, check_y)
                    #explosion_area.append((check_x, check_y))  # 障碍物位置也算在爆炸范围内
                    break
                #爆炸区域像素xy坐标以及rect
                self.explosion_area.append(pygame.Rect(check_x * TILE_SIZE, check_y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                #格子坐标
                explosion_area.append((check_x, check_y))
                #创建爆炸区域rect
                self.explosion_rect.append(pygame.Rect(check_x, check_y, TILE_SIZE, TILE_SIZE))
        #print("爆炸范围：", explosion_area)
        return explosion_area

    def destroy_blocks_in_explosion(self):
        explosion_area = []
        # 转换为格子坐标
        bomb_x = self.rect.x // TILE_SIZE
        bomb_y = self.rect.y // TILE_SIZE
        
        #上下左右
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]  
        #四向遍历
        for dx, dy in directions:
            for i in range(1, self.power + 1):
                check_x = bomb_x + dx * i
                check_y = bomb_y + dy * i                
                # 边界检查，地图左上角为(0,0),右下角为(len(map_obj.barrier_map[0])-1,len(map_obj.barrier_map)-1)
                # 若x<0则超左边界，x大于len(map_obj.barrier_map[0])-1则超右边界，
                # y<0则超上边界，y大于len(map_obj.barrier_map)-1则超下边界
                if (check_x < 0 or check_x >= len(self.map_obj.barrier_map[0]) or 
                    check_y < 0 or check_y >= len(self.map_obj.barrier_map)):
                    # 超出边界，跳出当前方向循环
                    break  
                # 障碍物检查
                if self.map_obj.barrier_map[check_y][check_x] != "empty":
                    # 遇到障碍物，记录摧毁的方块
                    self.destroyed_blocks.append((check_x, check_y))
                    #分离计算与摧毁，不然会造成贯穿摧毁
                    self.map_obj.remove_barrier(check_x, check_y)
                    self.map_obj.remove_collision(check_x, check_y)
                    break
    '''
    handle_explosion() 
    {
    1. calculate_explosion_area()     // 计算范围
    2. destroy_obstacles_in_area()   // 摧毁障碍物  
    3. check_chain_explosions()      // 检查连锁
    }
    '''
    def handle_explosion(self, bombs_group,players_group):
        if self.explosion_handled:
            return  # 已经处理过，避免重复处理
            
        self.explosion_handled = True

        # 获取爆炸范围
        explosion_area = self.get_explosion_area()
        
        # 检查连锁爆炸
        for bomb in bombs_group:
            if bomb != self and not bomb.exploded:  # 不是自己且未爆炸
                bomb_x = bomb.rect.x // TILE_SIZE
                bomb_y = bomb.rect.y // TILE_SIZE
        
                if (bomb_x, bomb_y) in explosion_area:
                    # 设置立即爆炸
                    bomb.trigger_explosion()
        '''
        # 弃用，逻辑该时玩家踩上爆炸区域就死，不是只有爆炸瞬间才炸死玩家
        # 遍历玩家
        for player in players_group:
            #遍历爆炸区域中每一单位爆炸矩形
            for rect in self.explosion_area:
                if player.feet_rect.colliderect(rect):
                    player.hit_by_bomb()
        '''
            
        # 最后摧毁爆炸范围内的障碍物，获取爆炸范围和连锁爆炸的处理要基于原始地图！
        self.destroy_blocks_in_explosion()

    def handle_bomb_exploded(self):
        self.timer+=1
        #放泡泡到炸之前
        if self.timer >= FPS*3.5 and not self.exploded:
            #爆炸持续时间,t/FPS=0.5s
            self.trigger_explosion()

        #泡泡开炸
        if self.exploded:
            self.explosion_timer-=1
            if self.explosion_timer<=0:
                #从bomb_group中移除
                self.kill()


    def draw(self, window):
        if not self.exploded:
            window.blit(self.image_bomb, self.rect.topleft)
        else:
            # 获取爆炸范围
            explosion_area = self.get_explosion_area() if self.map_obj else []
            
            # 中心爆炸
            pygame.draw.rect(window, (255, 100, 0), (self.rect.x, self.rect.y, TILE_SIZE, TILE_SIZE))
            
            # 根据实际爆炸范围绘制
            for x, y in explosion_area:
                pygame.draw.rect(window, (255, 100, 0), 
                                 (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))


