"""«interface» Search — contrato de búsqueda."""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .book_item import BookItem


class Search(ABC):
    @abstractmethod
    def search_by_title(self, title: str) -> List[BookItem]:
        ...

    @abstractmethod
    def search_by_author(self, author_name: str) -> List[BookItem]:
        ...

    @abstractmethod
    def search_by_isbn(self, isbn: str) -> List[BookItem]:
        ...
