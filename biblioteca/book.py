"""abstract class Book — clase abstracta base."""
from __future__ import annotations
from abc import ABC
from datetime import date
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .author import Author


class Book(ABC):
    """ISBN[0..1]{id}, title, summary, publisher, publication_date, pages, language."""

    def __init__(
        self,
        title: str,
        summary: str,
        publisher: str,
        publication_date: date,
        number_of_pages: int,
        language: str,
        isbn: Optional[str] = None,
    ):
        self.isbn = isbn
        self.title = title
        self.summary = summary
        self.publisher = publisher
        self.publication_date = publication_date
        self.number_of_pages = number_of_pages
        self.language = language
        # Multiplicidad 1..*: todo Book necesita >=1 Author (se valida aparte
        # para romper el ciclo de creación Book <-> Author).
        self._authors: List[Author] = []

    @property
    def authors(self) -> List[Author]:
        return list(self._authors)

    def add_author(self, author: Author) -> None:
        """Asociación 'wrote' — mantiene ambos lados consistentes."""
        if author not in self._authors:
            self._authors.append(author)
        if self not in author._books:
            author._books.append(self)

    def validate_multiplicity(self) -> None:
        if len(self._authors) < 1:
            raise ValueError(f"Book '{self.title}' requiere >=1 Author (1..*)")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(title={self.title!r})"
