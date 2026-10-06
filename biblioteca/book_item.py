"""«entity» BookItem — generalización de Book."""
from __future__ import annotations
from datetime import date
from typing import Optional, TYPE_CHECKING
from .book import Book

if TYPE_CHECKING:
    from .catalog import Catalog
    from .account import Account


class BookItem(Book):
    """Hereda de Book. Añade barcode{id}, tag RFID{id}, isReferenceOnly."""

    def __init__(
        self,
        title: str,
        summary: str,
        publisher: str,
        publication_date: date,
        number_of_pages: int,
        language: str,
        isbn: Optional[str] = None,
        barcode: Optional[str] = None,
        tag: Optional[str] = None,
        is_reference_only: bool = False,
        catalog: Optional[Catalog] = None,
    ):
        super().__init__(title, summary, publisher, publication_date,
                         number_of_pages, language, isbn)
        self.barcode = barcode
        self.tag = tag  # RFID modelado como str
        self.is_reference_only = is_reference_only
        self.borrowed_by: Optional[Account] = None
        self.reserved_by: Optional[Account] = None
        self._catalog: Optional[Catalog] = None
        if catalog is not None:
            # duck-typing para evitar import circular Catalog <-> BookItem
            catalog.add_item(self)

    @property
    def catalog(self) -> Optional[Catalog]:
        return self._catalog
