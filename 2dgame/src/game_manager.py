import os
import pygame
from player import Player
from map import  Map
from bomb import Bomb
import json
from config_loader import load_config, dict_controls

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

    def _init_window(self):
        width = self.config['windows']['window']['width']
        height = self.config['windows']['window']['height']
        self.window = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption(self.config['windows']['title'])


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
        player_1_config = self.config['players'][0]
        player_2_config = self.config['players'][1]
        player_controls = dict_controls(player_1_config['controls'])
        player2_controls = dict_controls(player_2_config['controls'])
        
        self.player = Player(
            id=player_1_config['id'],
            controls=player_controls,
            speed=player_1_config['speed'],
            speed_max=player_1_config['speed_max'],
            bombs_count=player_1_config['bomb_count'],
            bombs_max=player_1_config['bomb_max'],
            bomb_power=player_1_config['bomb_power'],
            bomb_power_max=player_1_config['bomb_power_max'],
            #读取贴图错误时使用红方块代替
            color=(255, 0, 0),
            game_mode=self.CURRENT_GAME_MODE,
            # 日后修改为传参
            x=player_1_config['spawn']['x'],
            y=player_1_config['spawn']['y'],
            sprite_name=self.config['assets']['sprites_name']['player_4'],

        )
        self.player2 = Player(
            id=player_2_config['id'],
            controls=player2_controls,
            speed=player_2_config['speed'],
            speed_max=player_2_config['speed_max'],
            bombs_count=player_2_config['bomb_count'],
            bombs_max=player_2_config['bomb_max'],
            bomb_power=player_2_config['bomb_power'],
            bomb_power_max=player_2_config['bomb_power_max'],
            color=(255, 0, 0),
            game_mode=self.CURRENT_GAME_MODE,
            # 日后修改为传参
            x=player_2_config['spawn']['x'],
            y=player_2_config['spawn']['y'],
            sprite_name=self.config['assets']['sprites_name']['player_1'],
        )
        
        # 创建 groups 并添加玩家
        self._init_groups()

    def _load_map_path(self,json_path,map_id):
        """从JSON文件加载地图数据"""
        with open(json_path, 'r', encoding='utf-8') as f:
            map_all=json.load(f)
            try:
                return   map_all[map_id]
            except KeyError:
                print(f"警告：地图ID {map_id} 不存在")
                return map_all[0]
            except json.JSONDecodeError:
                print(f"警告：无法加载地图文件 {json_path}")
                return None


    def _init_groups(self):
        self.players_group = pygame.sprite.Group()
        self.players_group.add(self.player)
        self.players_group.add(self.player2)
        self.bombs_group = pygame.sprite.Group()

        self.alive_count = len(self.players_group)

    def run(self):
        while self.running:
            self.clock.tick(self.config['windows']['fps'])
            self._handle_events()
            self._update()
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
        # 按 feet_y 排序 
        drawables.sort(key=lambda obj: obj[4])
        return drawables
    def _draw_sorted_obj(self,drawables):
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
                bomb_obj.draw(self.window)  # 传入地图对象用于爆炸范围计算


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
            for player_obj in self.players_group:
                player_obj.draw_debug_rect(self.window, self.DEBUG_MODE)
        # 更新显示
        if self.state =="ended":
            self._show_winner()
        pygame.display.update()

    def _update_player(self):
        '''更新玩家状态'''
        for player_obj in self.players_group:
            #玩家动作
            player_obj.move(self.map_obj.collision_rects)
            player_obj.place_bomb(self.bombs_group,self.map_obj)
            #玩家状态
            player_obj.update()
    def _update_bomb(self):
        for bomb in list(self.bombs_group):
            bomb.handle_bomb_exploded()  # 推进炸弹计时和爆炸状态
            if bomb.exploded and bomb.explosion_timer >= 29 and not bomb.explosion_handled:
                bomb.handle_explosion(self.bombs_group, self.players_group)  # 处理连锁爆炸和摧毁障碍物
    def _update_hit_explosion(self):
        # 命中判定：检测玩家是否在爆炸范围内
        for bomb in list(self.bombs_group):
            if bomb.exploded:
                for player_obj in self.players_group:
                    if player_obj.ifInExplosion(bomb.explosion_rect):
                        player_obj.hit_by_bomb(self.CURRENT_GAME_MODE)
                        self.alive_count = len(self.players_group)
    def _update(self):
        '''“输入→更新→碰撞/爆炸→伤害→渲染”的顺序执行'''
        # 更新玩家移动
        self._update_player()
        # 泡泡列表信息更新
        self._update_bomb()
        # 命中判定：检测玩家是否在爆炸范围内
        self._update_hit_explosion ()
        # 检查游戏状态
        self._check_game_state()

    def _check_game_state(self):
        """检查游戏状态：是否结束"""
        if self.state == "running":
            # 检查玩家是否死亡
            if self.alive_count <= 1:
                self.state = "ended"
                self.winner_id = self.players_group.sprites()[0].id
                return

    def _show_winner(self):
        """显示胜利者"""
        font = pygame.font.Font(None, 48)
        winner_text = f"Player {self.winner_id} wins! Press R to restart"
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

