from functools import partial, wraps
from collections import defaultdict


event_pool = defaultdict(list)


def register_action(func):
    event_pool[func.__name__].append(func)

    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


def whenever(action: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for effect in event_pool[func.__name__]:
                effect()
            return func(*args, **kwargs)

        return wrapper

    return decorator


def after(action: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator
