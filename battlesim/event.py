from functools import partial, wraps
from collections import defaultdict


event_pool = defaultdict(list)


class Event:
    def __init__(self, func, condition: str):
        self.func = func
        self.condition = condition

    def __call__(self, *args, **kwargs):
        self.func(*args, **kwargs)


def register_action(func):
    event_pool[func.__name__].append(func)

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        for minion, event in self.game.dispatcher.get(f"whenever_{func.__name__}", []):
            event(minion, self, *args, **kwargs)
        func(self, *args, **kwargs)
        for minion, event in self.game.dispatcher.get(f"after_{func.__name__}", []):
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
