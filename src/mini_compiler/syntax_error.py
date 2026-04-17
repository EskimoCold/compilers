from __future__ import annotations


class SyntaxErrorException(Exception):
    def __init__(
        self,
        message: str,
        position: int,
        line: int,
        column: int,
        cause: BaseException | None = None,
    ) -> None:
        super().__init__(message)
        self.__cause__ = cause
        self.position = position
        self.line = line
        self.column = column
