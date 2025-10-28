from math import e
import os
import yaml
import pygame

def load_config():
    config_path=os.path.join("..", "config", "config.yaml")
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def key_to_pygame(key_name:str):
    if isinstance(key_name, str):
        return key_name
    name=key_name.strip()
    if not name.startswith("K_"):
        raise ValueError(f"Invalid key name: {key_name}")
    try:
        return getattr(pygame.K, name)

    except AttributeError:
        raise ValueError(f"Invalid key name: {key_name}") from e

def dict_controls(controls_cfg):
    result = {}
    for key, value in controls_cfg.items():
        # 比如 name 是 "K_w"，转成 pygame.K_w
        result[key] = getattr(pygame, value)
    return result

'''--------------------测试区域------------------------------------------------------------------------------------------------'''
def main():
    config=load_config()

    player_1_config = config['players'][0]
    player_controls = player_1_config['controls']
    print(f"type(player_controls): {type(player_controls)}")
    print(f"player_controls: {player_controls}")

if __name__ == "__main__":
    main()
'''--------------------测试区域------------------------------------------------------------------------------------------------'''