import pygame
import os

from config_loader import load_config
config_sprite=load_config("config_sprite.yaml")
config_items=load_config("config_items.yaml")
def load_sprites():
    # 加载所有帧
    frames = []
    for i in range(1, 4):  # 假设文件名为frame_1.png到frame_3.png
        os.path.join("..", "assets", "sprites", "player")
        frame_path = os.path.join("..", "assets", "sprites", "player",f"manbo_sprite_{i}.png")
        frame = pygame.image.load(frame_path)
        frames.append(frame)

#弃用，不规则贴图组无法使用
def get_sprite(path,width,height,rows,cols,scale):
    #为了方便，直接返回二维数组
    try:
        sheet = pygame.image.load(os.path.join(path))
        sprites=[]
        
        for r in range(rows):
            row=[]
            for c in range(cols):
                surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
                rect = pygame.Rect(c*width, r*height, width, height)
                surface.blit(sheet, (0, 0), rect)

                if scale != 1:
                    width=int(surface.get_width() * scale)
                    height=int(surface.get_height() * scale)
                    surface=pygame.transform.scale(surface, (width, height))
                row.append(surface)
            sprites.append(row)
        return sprites
    except Exception as e:
        print(f"加载贴图失败: {e}")
        surf=pygame.Surface((width, height), pygame.SRCALPHA, 32)
        surf.fill((0,255,0))
        return surf
def output_sprites(sprites,name,path):
    for i in range(len(sprites)):
        for j in range(len(sprites[i])):
            pygame.image.save(sprites[i][j], os.path.join(path,f"{name}_{i}_{j}.png"))

def load_sprite_path(sprite_name):
    path="assets/sprites/player/idle"
    return path

def load_map():
    pass
#---------------------测试区--------------------------------------------------------------------
def main():
    pygame.init()
    pygame.display.set_mode((100, 100))

    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        while(1):
            key = pygame.key.get_pressed()
            print(key)

if __name__ == "__main__":
    main()


#---------------------测试区--------------------------------------------------------------------