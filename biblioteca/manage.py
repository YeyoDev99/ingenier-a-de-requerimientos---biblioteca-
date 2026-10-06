"""«interface» Manage — contrato de gestión."""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .book_item import BookItem


class Manage(ABC):
    @abstractmethod
    def add_book_item(self, item: BookItem) -> None:
        ...

    @abstractmethod
    def remove_book_item(self, item: BookItem) -> None:
        ...
