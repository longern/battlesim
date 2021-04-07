from typing import Generic, TypeVar

T = TypeVar("T")


class Tag(Generic[T]):
    default = None

    def __init__(self, default=None):
        self.default = default if default is not None else self.default

    def __set_name__(self, owner, name):
        self.private_name = "_" + name

    def __get__(self, obj, objtype=None) -> T:
        return getattr(obj, self.private_name, self.default)

    def __set__(self, obj, value):
        setattr(obj, self.private_name, value)


class BooleanTag(Tag[bool]):
    default = False

    def __set__(self, instance, value):
        if isinstance(value, str):
            value = int(str)
        setattr(instance, self.private_name, bool(value))


class IntegerTag(Tag[int]):
    default = 0

    def __set__(self, instance, value):
        setattr(instance, self.private_name, int(value))


class StringTag(Tag[str]):
    def __set__(self, instance, value):
        setattr(instance, self.private_name, str(value))
