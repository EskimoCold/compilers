from __future__ import annotations

from .type_info import TypeInfo


class TypeEnvironment:
    def __init__(self, parent: TypeEnvironment | None = None) -> None:
        self._parent = parent
        self._types: dict[str, TypeInfo] = {}

    def define(self, name: str, type_: TypeInfo) -> bool:
        if name in self._types:
            return False
        self._types[name] = type_
        return True

    def is_defined(self, name: str) -> bool:
        if name in self._types:
            return True
        if self._parent is not None:
            return self._parent.is_defined(name)
        return False

    def get(self, name: str) -> TypeInfo | None:
        if name in self._types:
            return self._types[name]
        if self._parent is not None:
            return self._parent.get(name)
        return None
