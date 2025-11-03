from math import e
import os
import yaml
import pygame

def load_config(config_name):
    config_path=os.path.join("..", "config", f"{config_name}")
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def dict_controls(controls_cfg):
    result = {}
    for key, value in controls_cfg.items():
        # 比如 value 是 "K_w"，转成 pygame.K_w
        result[key] = getattr(pygame, value)
    # 全部转换完，返回能直接使用的字典
    return result

'''--------------------测试区域------------------------------------------------------------------------------------------------'''
def main():
    pass

if __name__ == "__main__":
    pass

'''--------------------测试区域------------------------------------------------------------------------------------------------'''