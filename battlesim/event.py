from functools import wraps
from sys import intern


class Event:
    def __init__(self, func, condition: str):
        self.func = func
        self.condition = intern(condition)

    def __call__(self, *args, **kwargs):
        self.func(*args, **kwargs)


def register_action(func):
    whenever_action = intern(f"whenever_{func.__name__}")
    after_action = intern(f"after_{func.__name__}")

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        for minion, event in self.game.dispatcher[whenever_action]:
            event(minion, self, *args, **kwargs)
        func(self, *args, **kwargs)
        for minion, event in self.game.dispatcher[after_action]:
            event(minion, self, *args, **kwargs)

    return wrapper


def whenever(action: str):
    def decorator(func):
        action_name: str = action.__name__ if hasattr(action, "__name__") else action
        return Event(func, "whenever_" + action_name)

    return decorator


def after(action: str):
    def decorator(func):
        action_name: str = action.__name__ if hasattr(action, "__name__") else action
        return Event(func, "after_" + action_name)

    return decorator
