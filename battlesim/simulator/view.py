from functools import update_wrapper


class view:
    def __init__(self, func):
        update_wrapper(self, func)

    def __call__(self, iterable):
        return self.__wrapped__(iterable)

    def __ror__(self, iterable):
        return self.__wrapped__(iterable)
