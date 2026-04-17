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
from .token_type import TokenType


def format_tree(script: Script) -> str:
    lines: list[str] = ["program"]
    for stmt in script.statements:
        _tree_stmt(stmt, 1, lines)
    return "\n".join(lines)


def _ind(depth: int) -> str:
    return "  " * depth


def _tree_stmt(stmt: Stmt, depth: int, lines: list[str]) -> None:
    p = _ind(depth)

    if isinstance(stmt, VarStmt):
        lines.append(f"{p}var {stmt.name}")
        _tree_expr(stmt.init, depth + 1, lines)
    elif isinstance(stmt, AssignStmt):
        lines.append(f"{p}= {stmt.name}")
        _tree_expr(stmt.value, depth + 1, lines)
    elif isinstance(stmt, PrintStmt):
        lines.append(f"{p}print")
        _tree_expr(stmt.expr, depth + 1, lines)
    elif isinstance(stmt, BlockStmt):
        lines.append(f"{p}block")
        for s in stmt.statements:
            _tree_stmt(s, depth + 1, lines)
    elif isinstance(stmt, IfStmt):
        lines.append(f"{p}if")
        _tree_expr(stmt.condition, depth + 1, lines)
        _tree_stmt(stmt.then_branch, depth + 1, lines)
        if stmt.else_branch is not None:
            lines.append(f"{p}else")
            _tree_stmt(stmt.else_branch, depth + 1, lines)
    elif isinstance(stmt, WhileStmt):
        lines.append(f"{p}while")
        _tree_expr(stmt.condition, depth + 1, lines)
        _tree_stmt(stmt.body, depth + 1, lines)
    else:
        lines.append(f"{p}{stmt!r}")


def _tree_expr(expr: Expr, depth: int, lines: list[str]) -> None:
    p = _ind(depth)

    if isinstance(expr, NumberLiteral):
        lines.append(f"{p}{expr.value}")
        return
    if isinstance(expr, StringLiteral):
        lines.append(f"{p}{expr.value!r}")
        return
    if isinstance(expr, IdentifierExpr):
        lines.append(f"{p}{expr.name}")
        return
    if isinstance(expr, UnaryExpr):
        lines.append(f"{p}{_op_symbol(expr.op)}")
        _tree_expr(expr.operand, depth + 1, lines)
        return
    if isinstance(expr, BinaryExpr):
        lines.append(f"{p}{_op_symbol(expr.op)}")
        _tree_expr(expr.left, depth + 1, lines)
        _tree_expr(expr.right, depth + 1, lines)
        return
    if isinstance(expr, GroupExpr):
        _tree_expr(expr.inner, depth, lines)
        return
    lines.append(f"{p}{expr!r}")


def _op_symbol(op: TokenType) -> str:
    mapping = {
        TokenType.PLUS: "+",
        TokenType.MINUS: "-",
        TokenType.STAR: "*",
        TokenType.SLASH: "/",
        TokenType.EQEQ: "==",
        TokenType.NEQ: "!=",
        TokenType.LT: "<",
        TokenType.GT: ">",
        TokenType.LTEQ: "<=",
        TokenType.GTEQ: ">=",
        TokenType.AND: "&&",
        TokenType.OR: "||",
    }
    return mapping.get(op, str(op))
