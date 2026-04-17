from __future__ import annotations

from .ast_nodes import (
    AssignStmt,
    BinaryExpr,
    BlockStmt,
    Expr,
    GroupExpr,
    IdentifierExpr,
    IfStmt,
    NumberLiteral,
    PrintStmt,
    Script,
    Stmt,
    StringLiteral,
    UnaryExpr,
    VarStmt,
    WhileStmt,
)
from .source_position import get_line_column
from .syntax_error import SyntaxErrorException
from .token import Token
from .token_type import TokenType


class Parser:
    def __init__(self, tokens: list[Token], source_text: str | None = None) -> None:
        self._tokens = tokens
        self._source_text = source_text
        self._index = 0

    def parse(self) -> Script:
        statements: list[Stmt] = []
        while not self._is_at_end():
            statements.append(self._statement())
        return Script(tuple(statements))

    def _statement(self) -> Stmt:
        if self._match(TokenType.VAR):
            return self._parse_var_decl()

        if self._match(TokenType.PRINT):
            return self._parse_print()

        if self._match(TokenType.IF):
            return self._parse_if()

        if self._match(TokenType.WHILE):
            return self._parse_while()

        if self._match(TokenType.LBRACE):
            return self._parse_block()

        if self._check(TokenType.ID) and self._check_next(TokenType.EQ):
            return self._parse_assign()

        raise self._error(self._peek(), "Expected statement")

    def _parse_var_decl(self) -> Stmt:
        name = self._consume(TokenType.ID, "Expected variable name").value
        self._consume(TokenType.EQ, "Expected '='")
        init = self._parse_expression()
        self._consume(TokenType.SEMICOLON, "Expected ';' after variable declaration")
        return VarStmt(name, init)

    def _parse_assign(self) -> Stmt:
        name = self._consume(TokenType.ID, "Expected variable name").value
        self._consume(TokenType.EQ, "Expected '='")
        value = self._parse_expression()
        self._consume(TokenType.SEMICOLON, "Expected ';' after assignment")
        return AssignStmt(name, value)

    def _parse_print(self) -> Stmt:
        expr = self._parse_expression()
        self._consume(TokenType.SEMICOLON, "Expected ';' after print")
        return PrintStmt(expr)

    def _parse_if(self) -> Stmt:
        self._consume(TokenType.LPAREN, "Expected '(' after 'if'")
        cond = self._parse_expression()
        self._consume(TokenType.RPAREN, "Expected ')' after if condition")
        then_branch = self._statement()
        else_branch: Stmt | None = None
        if self._match(TokenType.ELSE):
            else_branch = self._statement()
        return IfStmt(cond, then_branch, else_branch)

    def _parse_while(self) -> Stmt:
        self._consume(TokenType.LPAREN, "Expected '(' after 'while'")
        cond = self._parse_expression()
        self._consume(TokenType.RPAREN, "Expected ')' after while condition")
        body = self._statement()
        return WhileStmt(cond, body)

    def _parse_block(self) -> Stmt:
        stmts: list[Stmt] = []
        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            stmts.append(self._statement())
        self._consume(TokenType.RBRACE, "Expected '}'")
        return BlockStmt(tuple(stmts))

    def _parse_expression(self) -> Expr:
        return self._parse_or()

    def _parse_or(self) -> Expr:
        left = self._parse_and()
        while self._match(TokenType.OR):
            op = self._previous().type
            right = self._parse_and()
            left = BinaryExpr(left, op, right)
        return left

    def _parse_and(self) -> Expr:
        left = self._parse_equality()
        while self._match(TokenType.AND):
            op = self._previous().type
            right = self._parse_equality()
            left = BinaryExpr(left, op, right)
        return left

    def _parse_equality(self) -> Expr:
        left = self._parse_comparison()
        while self._match(TokenType.EQEQ, TokenType.NEQ):
            op = self._previous().type
            right = self._parse_comparison()
            left = BinaryExpr(left, op, right)
        return left

    def _parse_comparison(self) -> Expr:
        left = self._parse_additive()
        while self._match(TokenType.LT, TokenType.GT, TokenType.LTEQ, TokenType.GTEQ):
            op = self._previous().type
            right = self._parse_additive()
            left = BinaryExpr(left, op, right)
        return left

    def _parse_additive(self) -> Expr:
        left = self._parse_multiplicative()
        while self._match(TokenType.PLUS, TokenType.MINUS):
            op = self._previous().type
            right = self._parse_multiplicative()
            left = BinaryExpr(left, op, right)
        return left

    def _parse_multiplicative(self) -> Expr:
        left = self._parse_unary()
        while self._match(TokenType.STAR, TokenType.SLASH):
            op = self._previous().type
            right = self._parse_unary()
            left = BinaryExpr(left, op, right)
        return left

    def _parse_unary(self) -> Expr:
        if self._match(TokenType.MINUS, TokenType.EXCL):
            op = self._previous().type
            right = self._parse_unary()
            return UnaryExpr(op, right)
        return self._parse_primary()

    def _parse_primary(self) -> Expr:
        if self._match(TokenType.NUMBER):
            try:
                v = float(self._previous().value)
                return NumberLiteral(v)
            except ValueError as ex:
                raise self._error(self._previous(), "Invalid numeric literal", ex) from ex

        if self._match(TokenType.STRING):
            return StringLiteral(self._previous().value)

        if self._match(TokenType.ID):
            return IdentifierExpr(self._previous().value)

        if self._match(TokenType.LPAREN):
            inner = self._parse_expression()
            self._consume(TokenType.RPAREN, "Expected ')' after expression")
            return GroupExpr(inner)

        raise self._error(self._peek(), "Expected expression")

    def _match(self, *types: TokenType) -> bool:
        for token_type in types:
            if not self._check(token_type):
                continue
            self._advance()
            return True
        return False

    def _check(self, typ: TokenType) -> bool:
        return not self._is_at_end() and self._peek().type == typ

    def _check_next(self, typ: TokenType) -> bool:
        return self._index + 1 < len(self._tokens) and self._tokens[self._index + 1].type == typ

    def _advance(self) -> Token:
        if not self._is_at_end():
            self._index += 1
        return self._previous()

    def _is_at_end(self) -> bool:
        return self._peek().type == TokenType.EOF

    def _peek(self) -> Token:
        if len(self._tokens) == 0:
            return Token(TokenType.EOF, "", 0)
        if self._index >= len(self._tokens):
            return self._tokens[-1]
        return self._tokens[self._index]

    def _previous(self) -> Token:
        if self._index == 0:
            return self._tokens[0] if len(self._tokens) > 0 else Token(TokenType.EOF, "", 0)
        return self._tokens[self._index - 1]

    def _consume(self, typ: TokenType, message: str) -> Token:
        if self._check(typ):
            return self._advance()
        raise self._error(self._peek(), message)

    def _error(
        self,
        token: Token,
        message: str,
        inner: BaseException | None = None,
    ) -> SyntaxErrorException:
        if self._source_text is not None:
            line, col = get_line_column(self._source_text, token.position)
            return SyntaxErrorException(
                f"{message} (line {line}, column {col})",
                token.position,
                line,
                col,
                inner,
            )
        return SyntaxErrorException(
            f"{message} (position {token.position})",
            token.position,
            0,
            0,
            inner,
        )
