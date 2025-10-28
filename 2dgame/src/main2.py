import pygame

from config_loader import load_config
from game_manager import GameManager


def main():
    config = load_config()
    game = GameManager(config)
    game.init()
    game.run()


if __name__ == "__main__":
    main()


