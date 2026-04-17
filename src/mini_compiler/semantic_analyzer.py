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
from .semantic_environment import SemanticEnvironment


class SemanticAnalyzer:
    def __init__(self) -> None:
        self._environment = SemanticEnvironment()
        self._errors: list[str] = []

    @property
    def errors(self) -> list[str]:
        return list(self._errors)

    def analyze(self, script: Script) -> list[str]:
        for statement in script.statements:
            self._visit_statement(statement)
        self._check_unused_variables()
        return self.errors

    def _visit_statement(self, statement: Stmt) -> None:
        if isinstance(statement, VarStmt):
            self._analyze_var_stmt(statement)
        elif isinstance(statement, AssignStmt):
            self._analyze_assign_stmt(statement)
        elif isinstance(statement, PrintStmt):
            self._analyze_print_stmt(statement)
        elif isinstance(statement, BlockStmt):
            self._analyze_block_stmt(statement)
        elif isinstance(statement, IfStmt):
            self._analyze_if_stmt(statement)
        elif isinstance(statement, WhileStmt):
            self._analyze_while_stmt(statement)
        else:
            self._errors.append(f"Unsupported statement: {type(statement).__name__}")

    def _visit_expression(self, expression: Expr) -> None:
        if isinstance(expression, NumberLiteral):
            return
        if isinstance(expression, StringLiteral):
            return
        if isinstance(expression, IdentifierExpr):
            self._analyze_identifier_expr(expression)
            return
        if isinstance(expression, BinaryExpr):
            self._analyze_binary_expr(expression)
            return
        if isinstance(expression, UnaryExpr):
            self._analyze_unary_expr(expression)
            return
        if isinstance(expression, GroupExpr):
            self._visit_expression(expression.inner)
            return
        self._errors.append(f"Unsupported expression: {type(expression).__name__}")

    def _analyze_var_stmt(self, stmt: VarStmt) -> None:
        if not self._environment.define_variable(stmt.name, is_initialized=False):
            self._errors.append(
                f"Variable '{stmt.name}' is already declared in this scope."
            )

        self._visit_expression(stmt.init)
        self._environment.set_initialized(stmt.name)

    def _analyze_assign_stmt(self, stmt: AssignStmt) -> None:
        self._visit_expression(stmt.value)

        if not self._environment.is_variable_defined(stmt.name):
            self._errors.append(
                f"Assignment to undeclared variable '{stmt.name}'."
            )
        else:
            self._environment.set_initialized(stmt.name)

    def _analyze_print_stmt(self, stmt: PrintStmt) -> None:
        self._visit_expression(stmt.expr)

    def _analyze_block_stmt(self, stmt: BlockStmt) -> None:
        previous_environment = self._environment
        self._environment = SemanticEnvironment(previous_environment)

        for inner in stmt.statements:
            self._visit_statement(inner)

        self._check_unused_variables()
        self._environment = previous_environment

    def _analyze_if_stmt(self, stmt: IfStmt) -> None:
        self._visit_expression(stmt.condition)
        self._visit_statement(stmt.then_branch)
        if stmt.else_branch is not None:
            self._visit_statement(stmt.else_branch)

    def _analyze_while_stmt(self, stmt: WhileStmt) -> None:
        self._visit_expression(stmt.condition)
        self._visit_statement(stmt.body)

    def _analyze_identifier_expr(self, expr: IdentifierExpr) -> None:
        symbol = self._environment.get_variable(expr.name)
        if symbol is None:
            self._errors.append(f"Use of undeclared variable '{expr.name}'.")
            return

        symbol.is_used = True
        if not symbol.is_initialized:
            self._errors.append(f"Use of uninitialized variable '{expr.name}'.")

    def _analyze_binary_expr(self, expr: BinaryExpr) -> None:
        self._visit_expression(expr.left)
        self._visit_expression(expr.right)

    def _analyze_unary_expr(self, expr: UnaryExpr) -> None:
        self._visit_expression(expr.operand)

    def _check_unused_variables(self) -> None:
        for symbol in self._environment.get_local_variables():
            if not symbol.is_used:
                self._errors.append(
                    f"[Semantic Warning] Variable '{symbol.name}' is declared but never used."
                )
