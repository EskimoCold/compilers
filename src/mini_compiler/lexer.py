from __future__ import annotations

from .token import Token
from .token_type import TokenType


class Lexer:
    def __init__(self, input_text: str) -> None:
        self._input = input_text
        self._length = len(input_text)
        self._position = 0

    def tokenize(self) -> list[Token]:
        result: list[Token] = []

        while self._position < self._length:
            current = self._peek()

            if current.isspace():
                self._next()
                continue

            if current.isdigit():
                self._tokenize_number(result)
                continue

            if current.isalpha():
                self._tokenize_word(result)
                continue

            if current == '"':
                self._tokenize_string(result)
                continue

            self._tokenize_operator(result)

        result.append(Token(TokenType.EOF, "", self._length))
        return result

    def _tokenize_number(self, result: list[Token]) -> None:
        start = self._position
        while self._peek().isdigit():
            self._next()
        number_str = self._input[start : self._position]
        result.append(Token(TokenType.NUMBER, number_str, start))

    def _tokenize_word(self, result: list[Token]) -> None:
        start = self._position
        while self._peek().isalnum():
            self._next()
        word = self._input[start : self._position]

        if word == "var":
            self._add_token(result, TokenType.VAR, word, start)
        elif word == "print":
            self._add_token(result, TokenType.PRINT, word, start)
        elif word == "if":
            self._add_token(result, TokenType.IF, word, start)
        elif word == "else":
            self._add_token(result, TokenType.ELSE, word, start)
        elif word == "while":
            self._add_token(result, TokenType.WHILE, word, start)
        else:
            self._add_token(result, TokenType.ID, word, start)

    def _tokenize_string(self, result: list[Token]) -> None:
        start = self._position
        self._next()  # opening "

        content_start = self._position
        while self._position < self._length and self._peek() != '"':
            self._next()

        if self._position >= self._length:
            raise RuntimeError(f"Unterminated string starting at position {start}")

        inner = self._input[content_start : self._position]
        self._next()  # closing "

        result.append(Token(TokenType.STRING, inner, start))

    def _tokenize_operator(self, result: list[Token]) -> None:
        current = self._peek()
        start = self._position

        if current == "(":
            self._next()
            self._add_token(result, TokenType.LPAREN, "(", start)
        elif current == ")":
            self._next()
            self._add_token(result, TokenType.RPAREN, ")", start)
        elif current == "{":
            self._next()
            self._add_token(result, TokenType.LBRACE, "{", start)
        elif current == "}":
            self._next()
            self._add_token(result, TokenType.RBRACE, "}", start)
        elif current == "+":
            self._next()
            self._add_token(result, TokenType.PLUS, "+", start)
        elif current == "-":
            self._next()
            self._add_token(result, TokenType.MINUS, "-", start)
        elif current == "*":
            self._next()
            self._add_token(result, TokenType.STAR, "*", start)
        elif current == "/":
            self._next()
            self._add_token(result, TokenType.SLASH, "/", start)
        elif current == ";":
            self._next()
            self._add_token(result, TokenType.SEMICOLON, ";", start)
        elif current == "=":
            if self._peek(1) == "=":
                self._next()
                self._next()
                self._add_token(result, TokenType.EQEQ, "==", start)
            else:
                self._next()
                self._add_token(result, TokenType.EQ, "=", start)
        elif current == "!":
            if self._peek(1) == "=":
                self._next()
                self._next()
                self._add_token(result, TokenType.NEQ, "!=", start)
            else:
                self._next()
                self._add_token(result, TokenType.EXCL, "!", start)
        elif current == "<":
            if self._peek(1) == "=":
                self._next()
                self._next()
                self._add_token(result, TokenType.LTEQ, "<=", start)
            else:
                self._next()
                self._add_token(result, TokenType.LT, "<", start)
        elif current == ">":
            if self._peek(1) == "=":
                self._next()
                self._next()
                self._add_token(result, TokenType.GTEQ, ">=", start)
            else:
                self._next()
                self._add_token(result, TokenType.GT, ">", start)
        elif current == "&":
            if self._peek(1) == "&":
                self._next()
                self._next()
                self._add_token(result, TokenType.AND, "&&", start)
            else:
                raise RuntimeError(f"Unexpected character '{current}' at position {self._position}")
        elif current == "|":
            if self._peek(1) == "|":
                self._next()
                self._next()
                self._add_token(result, TokenType.OR, "||", start)
            else:
                raise RuntimeError(f"Unexpected character '{current}' at position {self._position}")
        else:
            raise RuntimeError(f"Unexpected character '{current}' at position {self._position}")

    def _peek(self, offset: int = 0) -> str:
        i = self._position + offset
        if i >= self._length:
            return "\0"
        return self._input[i]

    def _next(self) -> str:
        if self._position >= self._length:
            return "\0"
        ch = self._input[self._position]
        self._position += 1
        return ch

    @staticmethod
    def _add_token(result: list[Token], typ: TokenType, value: str, start: int) -> None:
        result.append(Token(typ, value, start))
