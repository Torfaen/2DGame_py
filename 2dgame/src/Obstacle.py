TILE_SIZE=32
class ObstacleLayer:
    def __init__(self, collision_map):
        self.collision_map = collision_map

    def is_obstacle(self, x, y):
        """判断该位置是否有障碍物"""
        return self.collision_map[y // TILE_SIZE][x // TILE_SIZE] == 1
