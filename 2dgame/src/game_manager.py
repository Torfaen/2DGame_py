import os
import re
import pygame
import random
from player import Player
from map import Map
from bomb import Bomb
import json
from config_loader import load_config, dict_controls
from explosion import Explosion
from item import Item
from audio_manager import AudioManager

config=load_config("config.yaml")
config_character=load_config("config_character.yaml")
config_player=load_config("config_player.yaml")
config_tiles=load_config("config_tile.yaml")
TILE_SIZE=config["windows"]["tile_size"]

#“输入→更新→碰撞/爆炸→伤害→渲染”的顺序执行
class GameManager:
    def __init__(self, config):
        self.config = config
        self.map_obj = None
        self.player = None
        self.player2 = None
        self.bomb = None
        self.bombs_group = None
        self.players_group = None
        self.explosions_group = None
        self.items_group = None

        self.audio_manager = AudioManager()

        self.clock = None
        self.window = None
        self.running = True
        self.state = "running"
        self.winner_id = None

        self.DEBUG_MODE = config['windows']['debug']['DEBUG_MODE']
        self.GAMEMODE = config['game']['modes_allowed']
        self.CURRENT_GAME_MODE = config['game']['current_mode']
            
    def init(self):
        pygame.init()
        self._init_window()
        self._load_maps()
        self._load_players()
        self._init_groups()

    def _init_window(self):
        width = self.config['windows']['window']['width']
        height = self.config['windows']['window']['height']
        self.window = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption(self.config['windows']['title'])

    def _load_audio(self):
        self.audio_manager.load_sounds()
    
    def _load_maps(self):
        # 地图路径
        base_dir = self.config['assets']['base_dir']
        maps_config = self.config['assets']['maps']
        active_map_id = self.config['map']['active_id']
        
        floor_map_path = os.path.join(base_dir, maps_config['floor'])
        barrier_map_path = os.path.join(base_dir, maps_config['barrier'])
        collision_map_path = os.path.join(base_dir, maps_config['collision'])
        
        floor_map = self._load_map_path(floor_map_path, active_map_id)
        barrier_map = self._load_map_path(barrier_map_path, active_map_id)
        collision_map = self._load_map_path(collision_map_path, active_map_id)

        # 创建地图对象
        map_obj = Map()
        map_obj.set_floor_map(floor_map)
        map_obj.set_collision_map(collision_map)
        map_obj.set_barrier_map(barrier_map)
        self.map_obj = map_obj

    def _load_players(self):
                
        # 创建玩家对象
        player_1_config = config_player['player1']
        player_2_config = config_player['player2']
        player_controls = dict_controls(player_1_config['controls'])
        player2_controls = dict_controls(player_2_config['controls'])

        character_1_config = config_character['characters']['manbo']
        character_2_config = config_character['characters']['hajimi']
        self.player = Player(
            id=player_1_config['id'],
            controls=player_controls,
            speed=character_1_config['speed'],
            speed_max=character_1_config['speed_max'],
            bombs_count=character_1_config['bomb_count'],
            bombs_max=character_1_config['bomb_max'],
            bomb_power=character_1_config['bomb_power'],
            bomb_power_max=character_1_config['bomb_power_max'],
            #读取贴图错误时使用红方块代替
            color=(255, 0, 0),
            game_mode=self.CURRENT_GAME_MODE,
            # 日后修改为传参
            x=player_1_config['spawn']['x'],
            y=player_1_config['spawn']['y'],
            sprite_name=character_1_config['sprite'],

        )
        self.player2 = Player(
            id=player_2_config['id'],
            controls=player2_controls,
            speed=character_2_config['speed'],
            speed_max=character_2_config['speed_max'],
            bombs_count=character_2_config['bomb_count'],
            bombs_max=character_2_config['bomb_max'],
            bomb_power=character_2_config['bomb_power'],
            bomb_power_max=character_2_config['bomb_power_max'],
            color=(255, 0, 0),
            game_mode=self.CURRENT_GAME_MODE,
            # 日后修改为传参
            x=player_2_config['spawn']['x'],
            y=player_2_config['spawn']['y'],
            sprite_name=character_2_config['sprite'],
        )
        

    def _load_map_path(self,json_path,map_id):
        """从JSON文件加载地图数据"""
        with open(json_path, 'r', encoding='utf-8') as f:
            map_all=json.load(f)
            try:
                return   map_all[map_id]
            except KeyError:
                print(f"警告：地图ID {map_id} 不存在")
                return None
            except json.JSONDecodeError:
                print(f"警告：无法加载地图文件 {json_path}")
                return None


    def _init_groups(self):
        self.players_group = pygame.sprite.Group()
        self.players_group.add(self.player)
        self.players_group.add(self.player2)
        self.bombs_group = pygame.sprite.Group()
        self.explosions_group = pygame.sprite.Group()
        self.alive_count = len(self.players_group)
        self.items_group = pygame.sprite.Group()

    def run(self):
        while self.running:
            self.clock.tick(self.config['windows']['fps'])
            self._handle_events()
            self.update()
            self._render()
            pygame.display.update()
        pygame.quit()

    def _handle_draw_obj(self):
        drawables = []
        # 把地图物件加入列表
        for y in range(len(self.map_obj.barrier_map)):
            for x in range(len(self.map_obj.barrier_map[y])):
                if self.map_obj.barrier_map[y][x] == "empty":
                    continue
                tile_name = self.map_obj.barrier_map[y][x]
                pos_x = x * self.map_obj.tile_size
                pos_y = y * self.map_obj.tile_size
                # tile 高度=底部锚点
                feet_y = pos_y + self.map_obj.tile_size
                drawables.append(("tile", tile_name, pos_x, pos_y, feet_y))
        # 加入玩家
        for player_obj in self.players_group:
            drawables.append(("player", player_obj, player_obj.rect.x, player_obj.rect.y, player_obj.feet_rect.y))
        # 加入泡泡
        for bomb in self.bombs_group:
            drawables.append(("bomb", bomb, bomb.rect.x, bomb.rect.y, bomb.rect.y))
        # 加入爆炸区域
        for explosion in self.explosions_group:
            drawables.append(("explosion", explosion, explosion.rect.x, explosion.rect.y, explosion.rect.y))
        for item in self.items_group:
            drawables.append(("item", item, item.rect.x, item.rect.y, item.rect.y))
        # 按 feet_y 排序
        drawables.sort(key=lambda obj: obj[4])
        return drawables

    def _draw_sorted_obj(self,drawables):
        for obj in drawables:
            if obj[0] == "explosion":
                _, explosion, x, y, _ = obj
                explosion.draw(self.window)
        for obj in drawables:
            now_obj = obj
            kind = obj[0]
            if kind == "tile":
                _, tile_name, x, y, _ = obj
                self.map_obj.draw_tile(self.window, tile_name, x, y)
            elif kind == "player":
                _, p, _, _, _ = obj
                p.draw(self.window)
            elif kind == "bomb":
                _, bomb_obj, _, _, _ = obj
                bomb_obj.draw(self.window)  
            elif kind == "item":
                _, item_obj, _, _, _ = obj
                item_obj.draw(self.window)

    def _render(self):
        # 绘制画面
        self.window.fill((0, 0, 0))  # 清屏（黑色背景）
        self.map_obj.draw_floor(self.window)
        drawables = self._handle_draw_obj()
        self._draw_sorted_obj(drawables)

        # 绘制调试信息（在绘制完所有游戏对象之后，避免在循环内重复绘制）
        if self.DEBUG_MODE:
            self.map_obj.draw_debug_rect_barrier(self.window, self.DEBUG_MODE)
            self.map_obj.draw_debug_barrier_coords(self.window, self.DEBUG_MODE)  # 显示barrier坐标
            self.map_obj.draw_debug_rect_collision(self.window, self.DEBUG_MODE)
            for item_obj in self.items_group:
                item_obj.draw_debug_rect(self.window, self.DEBUG_MODE)
            for player_obj in self.players_group:
                player_obj.draw_debug_rect(self.window, self.DEBUG_MODE)
        # 更新显示
        if self.state =="ended":
            self._show_winner()
        pygame.display.update()
    
    def _update_player(self):
        '''更新玩家动作'''
        for player_obj in self.players_group:
            #玩家动作
            dx,dy=player_obj.handle_input()
            player_obj.move(dx,dy,self.map_obj.collision_rects)
            self.place_bomb(player_obj,self.bombs_group)
            #玩家状态
            player_obj.update()


    def place_bomb(self,player,bombs_group):
        """按键长按检测版：按下就尝试放置炸弹"""
        keys = pygame.key.get_pressed()
        if keys[player.controls["shift"]] and player.bomb_cooldown <= 0:
            self.create_bomb(player,bombs_group)

    def create_bomb(self,player,bombs_group):
        # 检查当前想激活的泡泡是否合法，移除已经爆炸的泡泡
        player.bombs_active = [b for b in player.bombs_active if not b.exploded]
        if len(player.bombs_active) >= player.bombs_count:
            return None
        grid_x,grid_y=player._get_feetgrid_position()
        x = grid_x * TILE_SIZE
        y = grid_y * TILE_SIZE
        for bomb in player.bombs_active:
            if bomb.rect.x == x and bomb.rect.y == y:
                return None
        
        bomb_new=Bomb(x,y,player.bomb_power,map_obj=self.map_obj)
        player.bombs_active.append(bomb_new)
        #合法的泡泡添加进容器
        bombs_group.add(bomb_new)
        #播放放置泡泡音效
        self.audio_manager.play("bomb_place")
        #放下泡泡，开始冷却
        player.bomb_cooldown = player.bomb_cooldown_max
        return bomb_new

    def _update_bomb(self):
        #统一创建explosion对象，避免重复创建
        for bomb in list(self.bombs_group):
            # 推进炸弹计时和爆炸状态
            bomb.update()
            if bomb.exploded  and not bomb.explosion_handled:
                # 触发爆炸，创建 Explosion 对象
                bomb.explosion_handled = True
                explosion = self.trigger_explosion(bomb)
                bomb._update_remove()
                self.audio_manager.play("explosion")
                self.explosions_group.add(explosion)


    def _update_item(self):
         for item in list(self.items_group):
            for player in list(self.players_group):
                if self._ifGetItem(player, item):          
                    item_effect = item.get_effect()
                    player.update_item_effect(item_effect)
                    item.alive = False
            item.update()


    # 爆炸类对象，统一由该函数创建，因为炸弹爆炸必定会产生爆炸区域，而爆炸区域在pvp中必定由炸弹产生
    def trigger_explosion(self,bomb):
        #创建该炸弹的爆炸区域对象
        bomb.alive = False
        bomb.remove_collision(bomb.rect.x, bomb.rect.y)
        #创建爆炸区域对象
        explosion = Explosion(bomb.rect.x, bomb.rect.y, bomb.power, self.map_obj)

        return explosion


    def hit_by_bomb(self, player,gamemode):
        # 或使用实际图像
        if gamemode == config["game"]["modes_allowed"][1]:
            player.alive = False
            player.status = "dead"
            player.die()

    def _update_explosion(self):
        for explosion in list(self.explosions_group):
            # 爆炸区域信息更新,推进爆炸水柱计时
            explosion.update()
            if not explosion.explosion_handled:
                # 连锁爆炸,同时加入连锁爆炸导致的爆炸区域列表
                self._handle_chain_explosion(explosion)
                # 标记已处理，避免重复处理
                explosion.explosion_handled = True
                # 然后再开始摧毁
                destroyed_blocks = self.get_destroy_blocks(explosion)
                self.handle_hit_blocks( destroyed_blocks)
        # 命中玩家判定，玩家会移动，需要爆炸时每帧判定，不要只在炸弹爆炸时判定
        if  self.explosions_group:
            self._update_hit_explosion()


    def handle_hit_blocks(self,destroyed_blocks):
        for block in destroyed_blocks:
           self._destroy_block(block)
           self._create_item(block)

    def _create_item(self,destroyed_block):
        # 掉落概率（比如30%）
        drop_rate = 0.3  # 可以放在配置文件中，或者在 __init__ 中初始化
        if random.random() < drop_rate:
            x_grid,y_grid= destroyed_block
            item = Item.create_random(x_grid*TILE_SIZE, y_grid*TILE_SIZE)
            self.items_group.add(item)

    def _handle_chain_explosion(self, explosion):
        # 连锁爆炸，遍历所有炸弹，如果炸弹在爆炸区域内，则触发连锁爆炸
        for bomb in list(self.bombs_group):
            if not bomb.exploded:  # 只处理未爆炸的炸弹
                bomb_grid_x = bomb.rect.x // TILE_SIZE
                bomb_grid_y = bomb.rect.y // TILE_SIZE
                
                if explosion.contains(bomb_grid_x, bomb_grid_y):
                    # 触发连锁爆炸
                    bomb.exploded = True
                    # 连锁爆炸产生的新爆炸区
       
    def _destroy_block(self,destroyed_block):
        x_grid,y_grid= destroyed_block
        self.map_obj.remove_collision(x_grid, y_grid)
        self.map_obj.remove_barrier(x_grid, y_grid)

            
    def get_destroy_blocks(self,explosion):
        #只记录需要摧毁的方块
        # 转换为格子坐标
        destroyed_blocks=[]
    
        e_grid_x=explosion.rect.x // TILE_SIZE
        e_grid_y=explosion.rect.y // TILE_SIZE

        #上下左右，四向算法，炸弹威力power与以下方向坐标组相乘，for循环从1格到power格遍历，获得一个炸弹所有爆炸区域的信息
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]  
        #四向遍历
        for dx, dy in directions:
            for i in range(1, explosion.power + 1):
                check_grid_x = e_grid_x + dx * i
                check_grid_y = e_grid_y + dy * i                
                # 边界检查，地图左上角为(0,0),右下角为(len(map_obj.barrier_map[0])-1,len(map_obj.barrier_map)-1)
                # 若x<0则超左边界，x大于len(map_obj.barrier_map[0])-1则超右边界，
                # y<0则超上边界，y大于len(map_obj.barrier_map)-1则超下边界
                if (check_grid_x < 0 or check_grid_x >= len(self.map_obj.barrier_map[0]) or 
                    check_grid_y < 0 or check_grid_y >= len(self.map_obj.barrier_map)):
                    # 超出边界，跳出当前方向循环
                    break  
                # 检查碰撞地图值：如果是2（不可摧毁），停止传播但不摧毁
                if (self.map_obj.collision_map and 
                    self.map_obj.collision_map[check_grid_y][check_grid_x] == 2):
                    # 遇到不可摧毁的障碍物，停止爆炸传播但不记录摧毁
                    break
                # 障碍物检查
                if self.map_obj.barrier_map[check_grid_y][check_grid_x] != "empty":
                    # 遇到可摧毁的障碍物，记录摧毁的方块
                    destroyed_blocks.append((check_grid_x, check_grid_y))
                    break
        return destroyed_blocks 
        #检查玩家是否捡起道具

    #处理删除物品

    #返回是否碰到物品
    def _ifGetItem(self, player,item):
        if not item:
            return False
        if player.hit_box.colliderect(item.hit_box):
            return True
        return False
    #处理玩家碰到道具后，获得的buff

    def _ifInExplosion(self,obj_rect, explosion_rects):
        if not explosion_rects:
            return False
        else:
            for rect in explosion_rects:
                rect_pixel=pygame.Rect(rect.x,rect.y,TILE_SIZE,TILE_SIZE)
                if obj_rect.hit_box.colliderect(rect_pixel):
                    return True
            return False

    def _get_explision_rects(self,explosions):
        explosions_rects = []
        for explosion in explosions:
            for gridxy in explosion.grids_info:
                grid_x,grid_y=gridxy['pos']
                explosion.rect=pygame.Rect(grid_x*TILE_SIZE,grid_y*TILE_SIZE,TILE_SIZE,TILE_SIZE)
                explosions_rects.append(explosion.rect)
        return explosions_rects

    def _update_hit_explosion(self):
        # 命中判定：检测玩家是否在爆炸范围内
        # 不要每帧判定，有explosion才判定
        # 所有的泡泡爆炸区域explosions_rects
        explosions_rects = self._get_explision_rects(self.explosions_group)
        for player_obj in self.players_group:
            if self._ifInExplosion(player_obj,explosions_rects):
                player_obj.hit_by_bomb(self.CURRENT_GAME_MODE)
                self.alive_count = len(self.players_group)
        for item_obj in self.items_group:
            if self._ifInExplosion(item_obj,explosions_rects):
                item_obj.alive = False
                self.items_group.remove(item_obj)
    #处理道具效果，根据道具名字做判断，道具效果生效


    def update(self):
        '''“输入→更新→碰撞/爆炸→伤害→渲染”的顺序执行'''
        # 更新玩家移动
        self._update_player()
        # 更新道具
        self._update_item()
        # 泡泡列表信息更新
        self._update_bomb()
        # 爆炸区域信息更新 , 爆炸击中玩家 , 摧毁方块
        self._update_explosion ()
        # 检查游戏状态
        self._check_game_state()

    def _check_game_state(self):
        """检查游戏状态：是否结束"""
        if self.state == "running":
            # 检查玩家是否死亡
            if self.alive_count <= 1:
                self.state = "ended"
                if self.alive_count == 0:
                    self.winner_id = None
                else:
                    self.winner_id = self.players_group.sprites()[0].id
                return

    def _show_winner(self):
        #
        if self.winner_id is not None:
            """显示胜利者"""
            font = pygame.font.Font(None, 48)
            winner_text = f"Player {self.winner_id} wins! Press R to restart"
            text_surface = font.render(winner_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(self.window.get_width()/2, self.window.get_height()/2))
        else:
            """显示平局"""
            font = pygame.font.Font(None, 48)
            winner_text = "no winner! Press R to restart"
            text_surface = font.render(winner_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(self.window.get_width()/2, self.window.get_height()/2))

        self.window.blit(text_surface, text_rect)

    def _restart_game(self):
        """重新开始游戏"""
        # 清理所有
        self.players_group.empty()
        self.bombs_group.empty()
        
        # 重新加载地图（如果需要恢复破坏的地形）
        self._load_maps()
        
        # 重新创建玩家并初始化 groups
        self._load_players()  # 里面会调用 _init_groups()
        self._init_groups()
        # 重置状态
        self.state = "running"
        self.alive_count = len(self.players_group)
        self.winner_id = None

    def _handle_events(self):
        """处理 pygame 输入事件，不包含游戏逻辑"""
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self.DEBUG_MODE = not self.DEBUG_MODE
                if event.key == pygame.K_r and self.state == "ended":
                    self._restart_game()

