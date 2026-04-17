from enum import Enum, auto


class TypeInfo(Enum):
    NUMBER = auto()
    STRING = auto()
    BOOL = auto()
    UNKNOWN = auto()

    def __str__(self) -> str:
        return self.name.lower()
