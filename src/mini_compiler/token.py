from dataclasses import dataclass

from .token_type import TokenType


@dataclass(frozen=True)
class Token:
    type: TokenType
    value: str
    position: int

    def __str__(self) -> str:
        return f"Token(Type: {self.type.name}, Value: '{self.value}') at {self.position}"
