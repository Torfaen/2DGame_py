import pygame
TILE_SIZE=32
class ExplosionLayer:
    def __init__(self):
        self.explosions = []

    def add_explosion(self, bomb):
        explosion = Explosion(bomb.rect.centerx, bomb.rect.centery, bomb.power)
        self.explosions.append(explosion)

    def update(self):
        for explosion in self.explosions:
            explosion.update()

    def draw(self, window):
        for explosion in self.explosions:
            explosion.draw(window)
class Explosion():
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
        center_rect = pygame.Rect(self.rect.x, self.rect.y, TILE_SIZE, TILE_SIZE)
        self.explosion_area.append(center_rect)

        # 向上扩展
        for i in range(1, self.power + 1):
            new_y = self.rect.y - i * TILE_SIZE
            grid_x = self.rect.x // TILE_SIZE
            grid_y = new_y // TILE_SIZE
            # 碰到障碍停止
            if collision_map[grid_y][grid_x] == 1:
                break
            self.explosion_area.append(pygame.Rect(self.rect.x, new_y, TILE_SIZE, TILE_SIZE))

        # 向下扩展
        for i in range(1, self.power + 1):
            new_y = self.rect.y + i * TILE_SIZE
            grid_x = self.rect.x // TILE_SIZE
            grid_y = new_y // TILE_SIZE
            if collision_map[grid_y][grid_x] == 1:
                break
            self.explosion_area.append(pygame.Rect(self.rect.x, new_y, TILE_SIZE, TILE_SIZE))

        # 向左扩展
        for i in range(1, self.power + 1):
            new_x = self.rect.x - i * TILE_SIZE
            grid_x = new_x // TILE_SIZE
            grid_y = self.rect.y // TILE_SIZE
            if collision_map[grid_y][grid_x] == 1:
                break
            self.explosion_area.append(pygame.Rect(new_x, self.rect.y, TILE_SIZE, TILE_SIZE))

        # 向右扩展
        for i in range(1, self.power + 1):
            new_x = self.rect.x + i * TILE_SIZE
            grid_x = new_x // TILE_SIZE
            grid_y = self.rect.y // TILE_SIZE
            if collision_map[grid_y][grid_x] == 1:
                break
            self.explosion_area.append(pygame.Rect(new_x, self.rect.y, TILE_SIZE, TILE_SIZE))

    def update(self):
        """更新爆炸状态"""
        if not self.exploded:
            self.exploded = True

    def draw(self, window):
        """绘制爆炸效果"""
        for rect in self.explosion_area:
            pygame.draw.rect(window, (255, 0, 0), rect)
