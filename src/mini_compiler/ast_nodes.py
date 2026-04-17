from __future__ import annotations

from abc import ABC
from dataclasses import dataclass

from .token_type import TokenType


class Expr(ABC):
    pass


@dataclass(frozen=True)
class NumberLiteral(Expr):
    value: float


@dataclass(frozen=True)
class StringLiteral(Expr):
    value: str


@dataclass(frozen=True)
class IdentifierExpr(Expr):
    name: str


@dataclass(frozen=True)
class UnaryExpr(Expr):
    op: TokenType
    operand: Expr


@dataclass(frozen=True)
class BinaryExpr(Expr):
    left: Expr
    op: TokenType
    right: Expr


@dataclass(frozen=True)
class GroupExpr(Expr):
    inner: Expr


class Stmt(ABC):
    pass


@dataclass(frozen=True)
class VarStmt(Stmt):
    name: str
    init: Expr


@dataclass(frozen=True)
class AssignStmt(Stmt):
    name: str
    value: Expr


@dataclass(frozen=True)
class PrintStmt(Stmt):
    expr: Expr


@dataclass(frozen=True)
class BlockStmt(Stmt):
    statements: tuple[Stmt, ...]


@dataclass(frozen=True)
class IfStmt(Stmt):
    condition: Expr
    then_branch: Stmt
    else_branch: Stmt | None


@dataclass(frozen=True)
class WhileStmt(Stmt):
    condition: Expr
    body: Stmt


@dataclass(frozen=True)
class Script:
    statements: tuple[Stmt, ...]
