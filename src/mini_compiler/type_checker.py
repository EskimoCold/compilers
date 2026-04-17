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
from .type_environment import TypeEnvironment
from .type_info import TypeInfo

_ARITHMETIC_OPS = {TokenType.PLUS, TokenType.MINUS, TokenType.STAR, TokenType.SLASH}
_COMPARISON_OPS = {TokenType.LT, TokenType.GT, TokenType.LTEQ, TokenType.GTEQ}
_EQUALITY_OPS = {TokenType.EQEQ, TokenType.NEQ}
_LOGICAL_OPS = {TokenType.AND, TokenType.OR}

_OP_SYMBOL = {
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
    TokenType.EXCL: "!",
}


class TypeChecker:
    def __init__(self) -> None:
        self._environment = TypeEnvironment()
        self._errors: list[str] = []

    @property
    def errors(self) -> list[str]:
        return list(self._errors)

    def check(self, script: Script) -> list[str]:
        for statement in script.statements:
            self._check_statement(statement)
        return self.errors

    def _check_statement(self, statement: Stmt) -> None:
        if isinstance(statement, VarStmt):
            self._check_var_stmt(statement)
        elif isinstance(statement, AssignStmt):
            self._check_assign_stmt(statement)
        elif isinstance(statement, PrintStmt):
            self._check_print_stmt(statement)
        elif isinstance(statement, BlockStmt):
            self._check_block_stmt(statement)
        elif isinstance(statement, IfStmt):
            self._check_if_stmt(statement)
        elif isinstance(statement, WhileStmt):
            self._check_while_stmt(statement)
        else:
            self._errors.append(f"Unsupported statement: {type(statement).__name__}")

    def _check_expression(self, expression: Expr) -> TypeInfo:
        if isinstance(expression, NumberLiteral):
            return TypeInfo.NUMBER
        if isinstance(expression, StringLiteral):
            return TypeInfo.STRING
        if isinstance(expression, IdentifierExpr):
            return self._check_identifier(expression)
        if isinstance(expression, BinaryExpr):
            return self._check_binary(expression)
        if isinstance(expression, UnaryExpr):
            return self._check_unary(expression)
        if isinstance(expression, GroupExpr):
            return self._check_expression(expression.inner)

        self._errors.append(f"Unsupported expression: {type(expression).__name__}")
        return TypeInfo.UNKNOWN

    def _check_var_stmt(self, stmt: VarStmt) -> None:
        init_type = self._check_expression(stmt.init)
        if not self._environment.define(stmt.name, init_type):
            self._errors.append(
                f"Variable '{stmt.name}' is already declared in this scope."
            )

    def _check_assign_stmt(self, stmt: AssignStmt) -> None:
        value_type = self._check_expression(stmt.value)
        declared = self._environment.get(stmt.name)

        if declared is None:
            self._errors.append(
                f"Assignment to undeclared variable '{stmt.name}'."
            )
            return

        if declared is TypeInfo.UNKNOWN or value_type is TypeInfo.UNKNOWN:
            return

        if declared is not value_type:
            self._errors.append(
                f"Type mismatch: cannot assign {value_type} to variable "
                f"'{stmt.name}' of type {declared}."
            )

    def _check_print_stmt(self, stmt: PrintStmt) -> None:
        self._check_expression(stmt.expr)

    def _check_block_stmt(self, stmt: BlockStmt) -> None:
        previous = self._environment
        self._environment = TypeEnvironment(previous)
        for inner in stmt.statements:
            self._check_statement(inner)
        self._environment = previous

    def _check_if_stmt(self, stmt: IfStmt) -> None:
        self._expect_bool(stmt.condition, "if")
        self._check_statement(stmt.then_branch)
        if stmt.else_branch is not None:
            self._check_statement(stmt.else_branch)

    def _check_while_stmt(self, stmt: WhileStmt) -> None:
        self._expect_bool(stmt.condition, "while")
        self._check_statement(stmt.body)

    def _check_identifier(self, expr: IdentifierExpr) -> TypeInfo:
        declared = self._environment.get(expr.name)
        if declared is None:
            self._errors.append(f"Use of undeclared variable '{expr.name}'.")
            return TypeInfo.UNKNOWN
        return declared

    def _check_binary(self, expr: BinaryExpr) -> TypeInfo:
        left = self._check_expression(expr.left)
        right = self._check_expression(expr.right)
        op = expr.op
        symbol = _OP_SYMBOL.get(op, op.name)

        if left is TypeInfo.UNKNOWN or right is TypeInfo.UNKNOWN:
            if op in _COMPARISON_OPS or op in _EQUALITY_OPS or op in _LOGICAL_OPS:
                return TypeInfo.BOOL
            return TypeInfo.UNKNOWN

        if op in _ARITHMETIC_OPS:
            if left is TypeInfo.NUMBER and right is TypeInfo.NUMBER:
                return TypeInfo.NUMBER
            self._errors.append(
                f"Operator '{symbol}' expects number operands, got {left} and {right}."
            )
            return TypeInfo.UNKNOWN

        if op in _COMPARISON_OPS:
            if left is TypeInfo.NUMBER and right is TypeInfo.NUMBER:
                return TypeInfo.BOOL
            self._errors.append(
                f"Operator '{symbol}' expects number operands, got {left} and {right}."
            )
            return TypeInfo.BOOL

        if op in _EQUALITY_OPS:
            if left is not right:
                self._errors.append(
                    f"Operator '{symbol}' requires operands of the same type, "
                    f"got {left} and {right}."
                )
            return TypeInfo.BOOL

        if op in _LOGICAL_OPS:
            if left is TypeInfo.BOOL and right is TypeInfo.BOOL:
                return TypeInfo.BOOL
            self._errors.append(
                f"Operator '{symbol}' expects boolean operands, got {left} and {right}."
            )
            return TypeInfo.BOOL

        self._errors.append(f"Unsupported binary operator: {symbol}")
        return TypeInfo.UNKNOWN

    def _check_unary(self, expr: UnaryExpr) -> TypeInfo:
        operand = self._check_expression(expr.operand)
        symbol = _OP_SYMBOL.get(expr.op, expr.op.name)

        if operand is TypeInfo.UNKNOWN:
            return TypeInfo.NUMBER if expr.op is TokenType.MINUS else TypeInfo.BOOL

        if expr.op is TokenType.MINUS:
            if operand is TypeInfo.NUMBER:
                return TypeInfo.NUMBER
            self._errors.append(
                f"Unary '{symbol}' expects a number operand, got {operand}."
            )
            return TypeInfo.UNKNOWN

        if expr.op is TokenType.EXCL:
            if operand is TypeInfo.BOOL:
                return TypeInfo.BOOL
            self._errors.append(
                f"Unary '{symbol}' expects a boolean operand, got {operand}."
            )
            return TypeInfo.BOOL

        self._errors.append(f"Unsupported unary operator: {symbol}")
        return TypeInfo.UNKNOWN

    def _expect_bool(self, condition: Expr, context: str) -> None:
        cond_type = self._check_expression(condition)
        if cond_type is TypeInfo.UNKNOWN or cond_type is TypeInfo.BOOL:
            return
        self._errors.append(
            f"Condition of '{context}' must be boolean, got {cond_type}."
        )
