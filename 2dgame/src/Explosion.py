import pygame
TILE_SIZE=32
class ExplosionLayer:
    def __init__(self):
        self.explosions = []

    def add_explosion(self, bomb):
        explosion = Explosion(bomb.rect.centerx, bomb.rect.centery, bomb.power)
        self.explosions.append(explosion)

    def update_explosion(self):
        for explosion in self.explosions:
            explosion.update()

    def draw_explosion(self, window):
        for explosion in self.explosions:
            explosion.draw(window)
class Explosion:
    def __init__(self, x, y, power):
        self.x = x
        self.y = y
        self.power = power
        self.exploded = False
        self.explosion_area = []

    def calculate_explosion_area(self, collision_map):
        """计算炸弹十字形爆炸区域，遇障碍物停止"""
        self.explosion_area = []

        # 中心格
        center_rect = pygame.Rect(self.x, self.y, TILE_SIZE, TILE_SIZE)
        self.explosion_area.append(center_rect)

        # 向上扩展
        for i in range(1, self.power + 1):
            new_y = self.y - i * TILE_SIZE
            grid_x = self.x // TILE_SIZE
            grid_y = new_y // TILE_SIZE
            # 碰到障碍停止
            if collision_map[grid_y][grid_x] == 1:
                break
            self.explosion_area.append(pygame.Rect(self.x, new_y, TILE_SIZE, TILE_SIZE))

        # 向下扩展
        for i in range(1, self.power + 1):
            new_y = self.y + i * TILE_SIZE
            grid_x = self.x // TILE_SIZE
            grid_y = new_y // TILE_SIZE
            if collision_map[grid_y][grid_x] == 1:
                break
            self.explosion_area.append(pygame.Rect(self.x, new_y, TILE_SIZE, TILE_SIZE))

        # 向左扩展
        for i in range(1, self.power + 1):
            new_x = self.x - i * TILE_SIZE
            grid_x = new_x // TILE_SIZE
            grid_y = self.y // TILE_SIZE
            if collision_map[grid_y][grid_x] == 1:
                break
            self.explosion_area.append(pygame.Rect(new_x, self.y, TILE_SIZE, TILE_SIZE))

        # 向右扩展
        for i in range(1, self.power + 1):
            new_x = self.x + i * TILE_SIZE
            grid_x = new_x // TILE_SIZE
            grid_y = self.y // TILE_SIZE
            if collision_map[grid_y][grid_x] == 1:
                break
            self.explosion_area.append(pygame.Rect(new_x, self.y, TILE_SIZE, TILE_SIZE))

    def update_explosion(self,collision_map,bombs_group):
        """更新爆炸状态"""
        if not self.exploded:
            self.exploded = True
            #爆炸区域检测
            self.calculate_explosion_area(collision_map)
            #连锁炸弹检测,当前泡泡与爆炸区域
            for bomb in bombs_group:
                if bomb.rect.collidelist(self.explosion_area)!=-1:
                    bomb.trigger_explosion()

    def draw(self, window):
        """绘制爆炸效果"""
        for rect in self.explosion_area:
            pygame.draw.rect(window, (255, 0, 0), rect)
