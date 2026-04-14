from config_loader import load_config
from game_manager import GameManager


class BombermanEnv:
    ACTIONS = (
        {"move": None, "bomb": False},
        {"move": "up", "bomb": False},
        {"move": "down", "bomb": False},
        {"move": "left", "bomb": False},
        {"move": "right", "bomb": False},
        {"move": None, "bomb": True},
    )

    def __init__(self, config=None, player_id=2, max_steps=1800, game_options=None):
        self.config = config or load_config("config.yaml")
        self.player_id = player_id
        self.max_steps = max_steps
        self.game_options = {
            "headless": True,
            "skip_menu": True,
            "render": False,
            "enable_audio": False,
            "human_controlled_ids": [],
        }
        if game_options:
            self.game_options.update(game_options)
        self.game = None
        self.steps = 0

    def reset(self):
        self.game = GameManager(self.config, options=self.game_options)
        self.game.init()
        self.steps = 0
        return self.get_observation()

    def step(self, action):
        if self.game is None:
            raise RuntimeError("Environment must be reset before stepping.")

        mapped_action = self._normalize_action(action)
        self.game.set_player_action(self.player_id, mapped_action)
        self.game.step_frame()
        self.steps += 1

        observation = self.get_observation()
        done = self.is_done()
        reward = self.compute_reward(done)
        info = self.get_info()
        return observation, reward, done, info

    def get_observation(self):
        snapshot = self.game.get_state_snapshot()
        snapshot["step"] = self.steps
        return snapshot

    def compute_reward(self, done):
        if not done:
            return 0.0
        if self.game.winner_id is None:
            return 0.0
        if self.game.winner_id == self.player_id:
            return 1.0
        return -1.0

    def is_done(self):
        return self.game.state == "ended" or self.steps >= self.max_steps

    def get_info(self):
        return {
            "winner_id": self.game.winner_id,
            "alive_count": self.game.alive_count,
            "steps": self.steps,
        }

    def _normalize_action(self, action):
        if isinstance(action, int):
            return self.ACTIONS[action]
        if isinstance(action, str):
            if action == "idle":
                return {"move": None, "bomb": False}
            if action == "bomb":
                return {"move": None, "bomb": True}
            return {"move": action, "bomb": False}
        return action
