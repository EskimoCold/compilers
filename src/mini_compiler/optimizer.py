from __future__ import annotations

from typing import Any

from .ast_nodes import (
    AssignStmt,
    BinaryExpr,
    BlockStmt,
    CallExpr,
    Expr,
    ExprStmt,
    FunctionStmt,
    GroupExpr,
    IdentifierExpr,
    IfStmt,
    NumberLiteral,
    PrintStmt,
    ReturnStmt,
    Script,
    Stmt,
    StringLiteral,
    UnaryExpr,
    VarStmt,
    WhileStmt,
)
from .token_type import TokenType


_UNRESOLVED: Any = object()


class DeadCodeOptimizer:
    def __init__(self) -> None:
        self._warnings: list[str] = []

    def optimize(self, script: Script) -> tuple[Script, list[str]]:
        self._warnings = []
        optimized_stmts = self._optimize_stmts(script.statements)
        return Script(tuple(optimized_stmts)), list(self._warnings)

    def _optimize_stmts(self, stmts: tuple[Stmt, ...]) -> list[Stmt]:
        result: list[Stmt] = []
        for i, stmt in enumerate(stmts):
            opt = self._optimize_stmt(stmt)
            if opt is not None:
                result.append(opt)
                if _always_returns(opt):
                    remaining = len(stmts) - i - 1
                    if remaining > 0:
                        self._warnings.append(
                            f"Dead code: {remaining} unreachable statement(s) "
                            f"after guaranteed return."
                        )
                    break

        return result

    def _optimize_stmt(self, stmt: Stmt) -> Stmt | None:
        if isinstance(stmt, IfStmt):
            return self._optimize_if(stmt)
        if isinstance(stmt, WhileStmt):
            return self._optimize_while(stmt)
        if isinstance(stmt, BlockStmt):
            return self._optimize_block(stmt)
        if isinstance(stmt, FunctionStmt):
            return self._optimize_function(stmt)
        return stmt

    def _optimize_if(self, stmt: IfStmt) -> Stmt | None:
        const = _try_fold(stmt.condition)

        if const is not _UNRESOLVED:
            if _is_truthy(const):
                self._warnings.append(
                    "Dead code: 'else' branch is unreachable "
                    "(condition is always true)."
                )
                return self._optimize_stmt(stmt.then_branch)
            else:
                if stmt.else_branch is None:
                    self._warnings.append(
                        "Dead code: 'if' body is unreachable "
                        "(condition is always false) — statement removed."
                    )
                    return None
                self._warnings.append(
                    "Dead code: 'if' body is unreachable "
                    "(condition is always false) — keeping 'else' branch."
                )
                return self._optimize_stmt(stmt.else_branch)

        opt_then = self._optimize_stmt(stmt.then_branch) or stmt.then_branch
        opt_else = (
            self._optimize_stmt(stmt.else_branch)
            if stmt.else_branch is not None
            else None
        )
        return IfStmt(stmt.condition, opt_then, opt_else)

    def _optimize_while(self, stmt: WhileStmt) -> Stmt | None:
        const = _try_fold(stmt.condition)
        if const is not _UNRESOLVED and not _is_truthy(const):
            self._warnings.append(
                "Dead code: 'while' body is unreachable "
                "(condition is always false) — loop removed."
            )
            return None
        opt_body = self._optimize_stmt(stmt.body) or stmt.body
        return WhileStmt(stmt.condition, opt_body)

    def _optimize_block(self, stmt: BlockStmt) -> BlockStmt:
        return BlockStmt(tuple(self._optimize_stmts(stmt.statements)))

    def _optimize_function(self, stmt: FunctionStmt) -> FunctionStmt:
        opt_body = self._optimize_block(stmt.body)
        return FunctionStmt(stmt.name, stmt.params, opt_body)


def _always_returns(stmt: Stmt) -> bool:
    if isinstance(stmt, ReturnStmt):
        return True
    if isinstance(stmt, BlockStmt):
        return any(_always_returns(s) for s in stmt.statements)
    if isinstance(stmt, IfStmt):
        if stmt.else_branch is None:
            return False
        return _always_returns(stmt.then_branch) and _always_returns(stmt.else_branch)
    return False


def _try_fold(expr: Expr) -> Any:
    if isinstance(expr, NumberLiteral):
        return expr.value
    if isinstance(expr, StringLiteral):
        return expr.value
    if isinstance(expr, GroupExpr):
        return _try_fold(expr.inner)
    if isinstance(expr, UnaryExpr):
        inner = _try_fold(expr.operand)
        if inner is _UNRESOLVED:
            return _UNRESOLVED
        if expr.op is TokenType.MINUS and isinstance(inner, (int, float)):
            return -inner
        if expr.op is TokenType.EXCL:
            return not _is_truthy(inner)
        return _UNRESOLVED
    if isinstance(expr, BinaryExpr):
        left = _try_fold(expr.left)
        right = _try_fold(expr.right)
        if left is _UNRESOLVED or right is _UNRESOLVED:
            return _UNRESOLVED
        op = expr.op
        try:
            if op is TokenType.PLUS:
                return left + right
            if op is TokenType.MINUS:
                return left - right
            if op is TokenType.STAR:
                return left * right
            if op is TokenType.SLASH:
                return _UNRESOLVED if right == 0 else left / right
            if op is TokenType.EQEQ:
                return left == right
            if op is TokenType.NEQ:
                return left != right
            if op is TokenType.LT:
                return left < right
            if op is TokenType.GT:
                return left > right
            if op is TokenType.LTEQ:
                return left <= right
            if op is TokenType.GTEQ:
                return left >= right
            if op is TokenType.AND:
                return _is_truthy(left) and _is_truthy(right)
            if op is TokenType.OR:
                return _is_truthy(left) or _is_truthy(right)
        except (TypeError, ValueError):
            pass
        return _UNRESOLVED
    return _UNRESOLVED


def _is_truthy(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    return bool(value)
