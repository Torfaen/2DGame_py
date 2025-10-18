from Explosion import ExplosionLayer
class BombManager:
    def __init__(self):
        self.bombs = []
        self.explosion_layer = ExplosionLayer()

    def add_bomb(self, bomb):
        self.bombs.append(bomb)

    def update(self, collision_map):
        for bomb in self.bombs:
            if bomb.exploded:
                self.explosion_layer.add_explosion(bomb)
                self.bombs.remove(bomb)
            bomb.handle_bomb_exploded()
        self.explosion_layer.update()

    def draw(self, window):
        for bomb in self.bombs:
            bomb.draw(window)
        self.explosion_layer.draw(window)
