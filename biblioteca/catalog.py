"""Catalog — asociación 'records' + interface realization Search/Manage."""
from __future__ import annotations
from typing import List, TYPE_CHECKING
from .search import Search
from .manage import Manage

if TYPE_CHECKING:
    from .book_item import BookItem
    from .library import Library


class Catalog(Search, Manage):
    """Catalog(1) --records-- (*) BookItem. Solo vive dentro de Library (composición)."""

    def __init__(self, library: Library):
        self._library = library
        self._items: List[BookItem] = []

    @property
    def library(self) -> Library:
        return self._library

    @property
    def items(self) -> List[BookItem]:
        return list(self._items)

    # --- Manage ---
    def add_item(self, item: BookItem) -> None:
        if item not in self._items:
            self._items.append(item)
            item._catalog = self

    def add_book_item(self, item: BookItem) -> None:
        self.add_item(item)

    def remove_book_item(self, item: BookItem) -> None:
        if item in self._items:
            self._items.remove(item)
            item._catalog = None

    # --- Search ---
    def search_by_title(self, title: str) -> List[BookItem]:
        q = title.lower()
        return [i for i in self._items if q in i.title.lower()]

    def search_by_author(self, author_name: str) -> List[BookItem]:
        q = author_name.lower()
        return [i for i in self._items
                if any(q in a.name.lower() for a in i.authors)]

    def search_by_isbn(self, isbn: str) -> List[BookItem]:
        return [i for i in self._items if i.isbn == isbn]

    def __repr__(self) -> str:
        return f"Catalog(items={len(self._items)})"
