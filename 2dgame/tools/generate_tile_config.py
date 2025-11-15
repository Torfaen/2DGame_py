import yaml
import os
import pygame

# 初始化pygame
pygame.init()  
# 生成配置文件
tiles_dir = os.path.join("..", "assets", "sprites", "background", "map_base")
output_path =os.path.join( "..", "config", "config_tile.yaml")
config_dir = os.path.dirname(output_path)

if os.path.exists(output_path):
    with open(output_path, 'r', encoding='utf-8') as f:
        #yaml内容解析为字典
        config = yaml.load(f, Loader=yaml.FullLoader) or {"tiles": {}}
else:
    config = {"tiles": {}}

tiles = os.listdir(tiles_dir)
for filename in tiles:
    if filename.endswith(".png"):
        tile_name = filename.replace(".png", "")
        tile_path = os.path.join(tiles_dir, filename)
        tile = pygame.image.load(tile_path)
        width, height = tile.get_size()
        
        # 如果已存在，保留原有的 anchor_x, anchor_y, collision
        if tile_name in config["tiles"]:
            tile_exist = config["tiles"][tile_name]
            #获取原有的anchor_x, anchor_y, collision，覆盖重新写入
            anchor_x = tile_exist.get("anchor_x", 0)
            anchor_y = tile_exist.get("anchor_y", 0)
            collision = tile_exist.get("collision", 0)
        else:
            # 新贴图使用默认值
            anchor_x = 0
            anchor_y = 0
            collision = 0

        config["tiles"][tile_name] = {
            "path": os.path.relpath(tile_path, config_dir).replace("\\", "/"),
            "width": width,
            "height": height,
            "anchor_x": anchor_x,
            "anchor_y": anchor_y,
            "collision": collision
        }
#写入yaml文件
with open(output_path, 'w', encoding='utf-8') as f:
    yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
print(f"已生成配置文件: {output_path}")

