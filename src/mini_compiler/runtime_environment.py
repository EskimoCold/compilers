from __future__ import annotations

from typing import Any


class RuntimeEnvironment:
    def __init__(self, parent: RuntimeEnvironment | None = None) -> None:
        self._parent = parent
        self._values: dict[str, Any] = {}

    def define(self, name: str, value: Any) -> None:
        self._values[name] = value

    def get(self, name: str) -> Any:
        if name in self._values:
            return self._values[name]
        if self._parent is not None:
            return self._parent.get(name)
        raise RuntimeError(f"Undefined variable '{name}'.")

    def set(self, name: str, value: Any) -> None:
        if name in self._values:
            self._values[name] = value
            return
        if self._parent is not None:
            self._parent.set(name, value)
            return
        raise RuntimeError(f"Assignment to undefined variable '{name}'.")
