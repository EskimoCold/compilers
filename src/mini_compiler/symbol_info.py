from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SymbolInfo:
    name: str
    is_initialized: bool = False
    is_used: bool = False
