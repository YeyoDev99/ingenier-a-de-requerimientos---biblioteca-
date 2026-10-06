"""Librarian — dependencias «use» a Search y Manage."""
from __future__ import annotations
from typing import List, TYPE_CHECKING
from .search import Search
from .manage import Manage

if TYPE_CHECKING:
    from .book_item import BookItem


class Librarian:
    def __init__(self, name: str, address: str, position: str):
        self.name = name
        self.address = address
        self.position = position

    def search(self, service: Search, title: str) -> List[BookItem]:
        return service.search_by_title(title)

    def register_book(self, service: Manage, item: BookItem) -> None:
        service.add_book_item(item)

    def remove_book(self, service: Manage, item: BookItem) -> None:
        service.remove_book_item(item)

    def __repr__(self) -> str:
        return f"Librarian(name={self.name!r}, position={self.position!r})"
