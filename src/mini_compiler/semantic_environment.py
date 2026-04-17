from __future__ import annotations

from .symbol_info import SymbolInfo


class SemanticEnvironment:
    def __init__(self, parent: SemanticEnvironment | None = None) -> None:
        self._parent = parent
        self._variables: dict[str, SymbolInfo] = {}

    def define_variable(self, name: str, is_initialized: bool) -> bool:
        if name in self._variables:
            return False
        self._variables[name] = SymbolInfo(name=name, is_initialized=is_initialized)
        return True

    def is_variable_defined(self, name: str) -> bool:
        if name in self._variables:
            return True
        if self._parent is not None:
            return self._parent.is_variable_defined(name)
        return False

    def get_variable(self, name: str) -> SymbolInfo | None:
        if name in self._variables:
            return self._variables[name]
        if self._parent is not None:
            return self._parent.get_variable(name)
        return None

    def set_initialized(self, name: str) -> None:
        symbol = self.get_variable(name)
        if symbol is not None:
            symbol.is_initialized = True

    def get_local_variables(self) -> list[SymbolInfo]:
        return list(self._variables.values())
