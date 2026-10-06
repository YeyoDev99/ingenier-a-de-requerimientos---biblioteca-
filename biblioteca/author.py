"""Clase Author — atributos name, biography."""
from __future__ import annotations
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .book import Book


class Author:
    def __init__(self, name: str, biography: str = ""):
        self.name = name
        self.biography = biography
        self._books: List[Book] = []  # lado Book de 'wrote' (1..*)

    @property
    def books(self) -> List[Book]:
        return list(self._books)

    def write(self, book: Book) -> None:
        """Reading order: Author wrote Book."""
        book.add_author(self)

    def validate_multiplicity(self) -> None:
        if len(self._books) < 1:
            raise ValueError(f"Author '{self.name}' requiere >=1 Book (1..*)")

    def __repr__(self) -> str:
        return f"Author(name={self.name!r})"
