from __future__ import annotations

from typing import Any, Callable

from .ast_nodes import (
    ArrayLiteral,
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
    IndexAssignStmt,
    IndexExpr,
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
from .runtime_environment import RuntimeEnvironment
from .token_type import TokenType


class ReturnException(Exception):
    def __init__(self, value: Any) -> None:
        self.value = value


class Interpreter:
    def __init__(self, output: Callable[[str], None] | None = None) -> None:
        self._environment = RuntimeEnvironment()
        self._output = output if output is not None else print

    def interpret(self, script: Script) -> None:
        for statement in script.statements:
            self.exec(statement)

    def exec(self, statement: Stmt) -> None:
        if isinstance(statement, VarStmt):
            self._exec_var(statement)
        elif isinstance(statement, AssignStmt):
            self._exec_assign(statement)
        elif isinstance(statement, PrintStmt):
            self._exec_print(statement)
        elif isinstance(statement, BlockStmt):
            self._exec_block(statement)
        elif isinstance(statement, IfStmt):
            self._exec_if(statement)
        elif isinstance(statement, WhileStmt):
            self._exec_while(statement)
        elif isinstance(statement, FunctionStmt):
            self._exec_function(statement)
        elif isinstance(statement, ReturnStmt):
            self._exec_return(statement)
        elif isinstance(statement, ExprStmt):
            self.eval(statement.expr)
        elif isinstance(statement, IndexAssignStmt):
            self._exec_index_assign(statement)
        else:
            raise RuntimeError(f"Unsupported statement: {type(statement).__name__}")

    def eval(self, expression: Expr) -> Any:
        if isinstance(expression, NumberLiteral):
            return expression.value
        if isinstance(expression, StringLiteral):
            return expression.value
        if isinstance(expression, IdentifierExpr):
            return self._environment.get(expression.name)
        if isinstance(expression, GroupExpr):
            return self.eval(expression.inner)
        if isinstance(expression, UnaryExpr):
            return self._eval_unary(expression)
        if isinstance(expression, BinaryExpr):
            return self._eval_binary(expression)
        if isinstance(expression, CallExpr):
            return self._eval_call(expression)
        if isinstance(expression, ArrayLiteral):
            return [self.eval(el) for el in expression.elements]
        if isinstance(expression, IndexExpr):
            return self._eval_index(expression)
        raise RuntimeError(f"Unsupported expression: {type(expression).__name__}")

    def _exec_var(self, stmt: VarStmt) -> None:
        value = self.eval(stmt.init)
        self._environment.define(stmt.name, value)

    def _exec_assign(self, stmt: AssignStmt) -> None:
        value = self.eval(stmt.value)
        self._environment.set(stmt.name, value)

    def _exec_print(self, stmt: PrintStmt) -> None:
        value = self.eval(stmt.expr)
        self._output(_stringify(value))

    def _exec_block(self, stmt: BlockStmt) -> None:
        previous = self._environment
        self._environment = RuntimeEnvironment(previous)
        try:
            for inner in stmt.statements:
                self.exec(inner)
        finally:
            self._environment = previous

    def _exec_if(self, stmt: IfStmt) -> None:
        if _is_truthy(self.eval(stmt.condition)):
            self.exec(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.exec(stmt.else_branch)

    def _exec_while(self, stmt: WhileStmt) -> None:
        while _is_truthy(self.eval(stmt.condition)):
            self.exec(stmt.body)

    def _exec_function(self, stmt: FunctionStmt) -> None:
        self._environment.define_function(stmt.name, stmt)

    def _exec_return(self, stmt: ReturnStmt) -> None:
        value = self.eval(stmt.value) if stmt.value is not None else None
        raise ReturnException(value)

    def _eval_call(self, expr: CallExpr) -> Any:
        func_decl = self._environment.get_function(expr.callee_name)
        args = [self.eval(arg) for arg in expr.arguments]

        call_env = RuntimeEnvironment(self._environment)
        for i, param in enumerate(func_decl.params):
            call_env.define(param, args[i] if i < len(args) else None)

        previous_env = self._environment
        self._environment = call_env
        try:
            for inner_stmt in func_decl.body.statements:
                self.exec(inner_stmt)
        except ReturnException as ret:
            return ret.value
        finally:
            self._environment = previous_env
        return None

    def _exec_index_assign(self, stmt: IndexAssignStmt) -> None:
        array = self._environment.get(stmt.array_name)
        if not isinstance(array, list):
            raise RuntimeError(
                f"Cannot index non-array value '{stmt.array_name}'."
            )
        index = self.eval(stmt.index)
        if not isinstance(index, (int, float)) or isinstance(index, bool):
            raise RuntimeError("Array index must be a number.")
        i = int(index)
        if i < 0 or i >= len(array):
            raise RuntimeError(
                f"Index {i} out of bounds for array of length {len(array)}."
            )
        array[i] = self.eval(stmt.value)

    def _eval_index(self, expr: IndexExpr) -> Any:
        array = self.eval(expr.array)
        if not isinstance(array, list):
            raise RuntimeError("Cannot index a non-array value.")
        index = self.eval(expr.index)
        if not isinstance(index, (int, float)) or isinstance(index, bool):
            raise RuntimeError("Array index must be a number.")
        i = int(index)
        if i < 0 or i >= len(array):
            raise RuntimeError(
                f"Index {i} out of bounds for array of length {len(array)}."
            )
        return array[i]

    def _eval_unary(self, expr: UnaryExpr) -> Any:
        operand = self.eval(expr.operand)
        if expr.op is TokenType.MINUS:
            _expect_number(operand, "-")
            return -operand
        if expr.op is TokenType.EXCL:
            return not _is_truthy(operand)
        raise RuntimeError(f"Unsupported unary operator: {expr.op.name}")

    def _eval_binary(self, expr: BinaryExpr) -> Any:
        op = expr.op

        if op is TokenType.AND:
            left = self.eval(expr.left)
            if not _is_truthy(left):
                return False
            return _is_truthy(self.eval(expr.right))

        if op is TokenType.OR:
            left = self.eval(expr.left)
            if _is_truthy(left):
                return True
            return _is_truthy(self.eval(expr.right))

        left = self.eval(expr.left)
        right = self.eval(expr.right)

        if op is TokenType.PLUS:
            _expect_number(left, "+")
            _expect_number(right, "+")
            return left + right
        if op is TokenType.MINUS:
            _expect_number(left, "-")
            _expect_number(right, "-")
            return left - right
        if op is TokenType.STAR:
            _expect_number(left, "*")
            _expect_number(right, "*")
            return left * right
        if op is TokenType.SLASH:
            _expect_number(left, "/")
            _expect_number(right, "/")
            if right == 0:
                raise RuntimeError("Division by zero.")
            return left / right

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

        raise RuntimeError(f"Unsupported binary operator: {op.name}")


def _is_truthy(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    return bool(value)


def _expect_number(value: Any, op: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise RuntimeError(f"Operator '{op}' expects a number, got {_type_name(value)}.")


def _type_name(value: Any) -> str:
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, (int, float)):
        return "number"
    if isinstance(value, str):
        return "string"
    return type(value).__name__


def _stringify(value: Any) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    if isinstance(value, list):
        return "[" + ", ".join(_stringify(v) for v in value) + "]"
    return str(value)
