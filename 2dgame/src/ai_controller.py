import random


class BaseAIController:
    def decide(self, observation):
        raise NotImplementedError()


class RandomAIController(BaseAIController):
    ACTIONS = (
        {"move": None, "bomb": False},
        {"move": "up", "bomb": False},
        {"move": "down", "bomb": False},
        {"move": "left", "bomb": False},
        {"move": "right", "bomb": False},
        {"move": None, "bomb": True},
    )

    def decide(self, observation):
        return random.choice(self.ACTIONS)
