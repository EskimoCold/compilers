from enum import Enum, auto


class TokenType(Enum):
    NUMBER = auto()
    ID = auto()
    STRING = auto()
    VAR = auto()

    PRINT = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()

    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    EQ = auto()
    EQEQ = auto()
    EXCL = auto()
    NEQ = auto()
    LT = auto()
    GT = auto()
    LTEQ = auto()
    GTEQ = auto()
    AND = auto()
    OR = auto()

    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    SEMICOLON = auto()

    EOF = auto()
