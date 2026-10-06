"""
Sistema de Biblioteca - Implementación en Python del diagrama UML de clases.

Mapeo del diagrama:
- Book: abstract class
- Book Item: «entity» + generalización de Book
- Account: «entity»
- AccountState: enumeration data type + dependencia «use» desde Account
- Author, Library, Catalog, Patron, Librarian: clases normales
- Search, Manage: «interface» + interface realization desde Catalog
- Relaciones: asociación, agregación, composición, multiplicidad, reading order,
  usage dependency, atributos, clase estereotipada.

Autor: Modelado desde Ingeniería de Requerimientos
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import List, Optional


# ---------------------------------------------------------------------------
# enumeration data type: AccountState
# ---------------------------------------------------------------------------
class AccountState(Enum):
    """«enumeration» AccountState."""
    ACTIVE = "Active"
    FROZEN = "Frozen"
    CLOSED = "Closed"


# ---------------------------------------------------------------------------
# Clases abstractas / interfaces
# ---------------------------------------------------------------------------
class Book(ABC):
    """
    abstract class Book.
    Atributos: ISBN {id} [0..1], title, summary, publisher,
               publication_date, number_of_pages, language.
    Relación 'wrote' con Author: 1..* <-> 1..* (many-to-many, reading order Book -> Author).
    """

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
        self.isbn: Optional[str] = isbn  # String[0..1] {id}
        self.title: str = title
        self.summary: str = summary
        self.publisher: str = publisher
        self.publication_date: date = publication_date
        self.number_of_pages: int = number_of_pages
        self.language: str = language
        # Multiplicidad 1..* del lado Author: todo Book debe tener >=1 Author.
        # Se mantiene la lista vacía al inicio y se exige via add_author para
        # romper la dependencia circular de creación Book <-> Author.
        self._authors: List[Author] = []

    @property
    def authors(self) -> List[Author]:
        return list(self._authors)

    def add_author(self, author: Author) -> None:
        """Mantiene consistencia bidireccional de 'wrote'."""
        if author not in self._authors:
            self._authors.append(author)
        if self not in author._books:
            author._books.append(self)

    def validate_multiplicity(self) -> None:
        if len(self._authors) < 1:
            raise ValueError(f"Book '{self.title}' debe tener al menos 1 Author (1..*)")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(isbn={self.isbn!r}, title={self.title!r})"


class Author:
    """Clase Author. Atributos: name, biography."""

    def __init__(self, name: str, biography: str = ""):
        self.name: str = name
        self.biography: str = biography
        # Lado Book de 'wrote': 1..*
        self._books: List[Book] = []

    @property
    def books(self) -> List[Book]:
        return list(self._books)

    def write(self, book: Book) -> None:
        """Reading order: Author <-wrote- Book. 'wrote' se lee Author wrote Book."""
        book.add_author(self)

    def validate_multiplicity(self) -> None:
        if len(self._books) < 1:
            raise ValueError(f"Author '{self.name}' debe haber escrito al menos 1 Book (1..*)")

    def __repr__(self) -> str:
        return f"Author(name={self.name!r})"


# ---------------------------------------------------------------------------
# «entity» Book Item — generalización de Book
# ---------------------------------------------------------------------------
class BookItem(Book):
    """
    «entity» Book Item.
    Generalización: BookItem --|> Book (hereda todos los atributos de Book).
    Atributos propios: barcode {id} [0..1], tag: RFID [0..1] {id}, is_reference_only.
    Asociaciones:
      - Catalog (1) -- records -- (*) BookItem
      - Account -- borrowed (0..12) / reserved (0..3) -- BookItem
    """

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
        tag: Optional[str] = None,  # RFID modelado como str
        is_reference_only: bool = False,
        catalog: Optional[Catalog] = None,
    ):
        super().__init__(title, summary, publisher, publication_date,
                         number_of_pages, language, isbn)
        self.barcode: Optional[str] = barcode
        self.tag: Optional[str] = tag
        self.is_reference_only: bool = is_reference_only
        self.borrowed_by: Optional[Account] = None
        self.reserved_by: Optional[Account] = None
        self._catalog: Optional[Catalog] = None
        if catalog is not None:
            catalog.add_item(self)

    @property
    def catalog(self) -> Optional[Catalog]:
        return self._catalog

    def __repr__(self) -> str:
        return f"BookItem(barcode={self.barcode!r}, title={self.title!r})"


# ---------------------------------------------------------------------------
# «entity» Account
# ---------------------------------------------------------------------------
class Account:
    """
    «entity» Account.
    Atributos: number {id}, history[0..*], opened: Date, state: AccountState.
    Dependencia «use»: Account --> AccountState (usa la enumeración).
    Asociaciones borrowed 0..12 y reserved 0..3 hacia BookItem.
    Agregación: Library (1) <>-- (*) Account, rol 'accounts'.
    Asociación 'account' con Patron.
    """

    MAX_BORROWED = 12  # multiplicidad 0..12
    MAX_RESERVED = 3   # multiplicidad 0..3

    def __init__(
        self,
        number: str,
        opened: date,
        state: AccountState = AccountState.ACTIVE,
        history: Optional[List[str]] = None,
    ):
        self.number: str = number  # {id}
        self.history: List[str] = history if history is not None else []
        self.opened: date = opened
        self.state: AccountState = state  # «use» de la enumeración
        self._borrowed: List[BookItem] = []
        self._reserved: List[BookItem] = []
        self.patron: Optional[Patron] = None  # navegabilidad inversa de 'account'

    @property
    def borrowed(self) -> List[BookItem]:
        return list(self._borrowed)

    @property
    def reserved(self) -> List[BookItem]:
        return list(self._reserved)

    def _check_open(self) -> None:
        if self.state == AccountState.CLOSED:
            raise ValueError(f"Account {self.number} está Closed, no puede operar.")
        if self.state == AccountState.FROZEN:
            raise ValueError(f"Account {self.number} está Frozen, operación bloqueada.")

    def borrow(self, item: BookItem) -> None:
        """Asociación 'borrowed' 0..12."""
        self._check_open()
        if item.is_reference_only:
            raise ValueError("El ejemplar es de referencia (isReferenceOnly=True).")
        if item.borrowed_by is not None:
            raise ValueError("El ejemplar ya está prestado.")
        if len(self._borrowed) >= self.MAX_BORROWED:
            raise ValueError("Multiplicidad violada: máximo 12 prestados (0..12).")
        self._borrowed.append(item)
        item.borrowed_by = self
        self.history.append(f"borrowed {item.barcode}")

    def reserve(self, item: BookItem) -> None:
        """Asociación 'reserved' 0..3."""
        self._check_open()
        if len(self._reserved) >= self.MAX_RESERVED:
            raise ValueError("Multiplicidad violada: máximo 3 reservados (0..3).")
        if item in self._reserved:
            raise ValueError("El ejemplar ya está reservado por esta cuenta.")
        self._reserved.append(item)
        item.reserved_by = self
        self.history.append(f"reserved {item.barcode}")

    def return_item(self, item: BookItem) -> None:
        if item in self._borrowed:
            self._borrowed.remove(item)
            item.borrowed_by = None
            self.history.append(f"returned {item.barcode}")

    def __repr__(self) -> str:
        return f"Account(number={self.number!r}, state={self.state.value})"


# ---------------------------------------------------------------------------
# Library — agregación y composición
# ---------------------------------------------------------------------------
class Library:
    """
    Library(name, address).
    - Agregación (rombo blanco): Library 1 <>-- * Account (rol 'accounts').
      Account puede existir sin Library.
    - Composición (rombo negro): Library 1 <♦-- Catalog.
      Catalog no existe sin Library (ciclo de vida dependiente).
    """

    def __init__(self, name: str, address: str):
        self.name: str = name
        self.address: str = address
        self._accounts: List[Account] = []  # agregación
        # composición: la Library crea y posee su Catalog
        self._catalog: Catalog = Catalog(library=self)

    @property
    def accounts(self) -> List[Account]:
        return list(self._accounts)

    @property
    def catalog(self) -> Catalog:
        return self._catalog

    def add_account(self, account: Account) -> None:
        """Agregación: vincula una cuenta existente."""
        if account not in self._accounts:
            self._accounts.append(account)

    def remove_account(self, account: Account) -> None:
        """Agregación: al removerla de Library, el objeto Account sigue vivo."""
        if account in self._accounts:
            self._accounts.remove(account)

    def __repr__(self) -> str:
        return f"Library(name={self.name!r}, accounts={len(self._accounts)})"


# ---------------------------------------------------------------------------
# «interface» Search / Manage + interface realization en Catalog
# ---------------------------------------------------------------------------
class Search(ABC):
    """«interface» Search. Dependencias «use» desde Patron y Librarian."""

    @abstractmethod
    def search_by_title(self, title: str) -> List[BookItem]:
        ...

    @abstractmethod
    def search_by_author(self, author_name: str) -> List[BookItem]:
        ...

    @abstractmethod
    def search_by_isbn(self, isbn: str) -> List[BookItem]:
        ...


class Manage(ABC):
    """«interface» Manage. Dependencia «use» desde Librarian."""

    @abstractmethod
    def add_book_item(self, item: BookItem) -> None:
        ...

    @abstractmethod
    def remove_book_item(self, item: BookItem) -> None:
        ...


class Catalog(Search, Manage):
    """
    Catalog.
    - Asociación 'records': Catalog (1) -- (*) BookItem.
    - Interface realization (triángulo punteado): Catalog ..|> Search, Manage.
    - Composición: solo existe dentro de una Library.
    """

    def __init__(self, library: Library):
        self._library: Library = library  # parte de la composición
        self._items: List[BookItem] = []

    @property
    def library(self) -> Library:
        return self._library

    @property
    def items(self) -> List[BookItem]:
        return list(self._items)

    # --- Manage (realization) ---
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

    # --- Search (realization) ---
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


# ---------------------------------------------------------------------------
# Patron / Librarian — usage dependency «use»
# ---------------------------------------------------------------------------
class Patron:
    """
    Patron(name, address).
    - Asociación 'account': Patron tiene 1 Account.
    - Dependencia «use»: Patron ..> Search (usa la interfaz, no la posee).
    """

    def __init__(self, name: str, address: str, account: Account):
        self.name: str = name
        self.address: str = address
        self.account: Account = account
        account.patron = self

    def search(self, search_service: Search, title: str) -> List[BookItem]:
        """«use» Search: solo necesita el contrato de la interfaz."""
        return search_service.search_by_title(title)

    def __repr__(self) -> str:
        return f"Patron(name={self.name!r})"


class Librarian:
    """
    Librarian(name, address, position).
    Dependencias «use»: Librarian ..> Search, Librarian ..> Manage.
    """

    def __init__(self, name: str, address: str, position: str):
        self.name: str = name
        self.address: str = address
        self.position: str = position

    def search(self, search_service: Search, title: str) -> List[BookItem]:
        return search_service.search_by_title(title)

    def register_book(self, manage_service: Manage, item: BookItem) -> None:
        manage_service.add_book_item(item)

    def remove_book(self, manage_service: Manage, item: BookItem) -> None:
        manage_service.remove_book_item(item)

    def __repr__(self) -> str:
        return f"Librarian(name={self.name!r}, position={self.position!r})"


# ---------------------------------------------------------------------------
# Demo de verificación (multiplicidades y relaciones)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    lib = Library(name="Biblioteca Central", address="Av. Principal 123")
    author = Author(name="G. Márquez", biography="Escritor")
    item = BookItem(
        title="Cien años de soledad",
        summary="Novela",
        publisher="Sudamericana",
        publication_date=date(1967, 5, 30),
        number_of_pages=471,
        language="ES",
        isbn="978-3-16-148410-0",
        barcode="B-0001",
        tag="RFID-0001",
        catalog=lib.catalog,
    )
    author.write(item)
    item.validate_multiplicity()
    author.validate_multiplicity()

    acc = Account(number="A-1", opened=date.today(), state=AccountState.ACTIVE)
    lib.add_account(acc)
    acc.borrow(item)

    patron = Patron(name="Ana", address="Calle 1", account=acc)
    librarian = Librarian(name="Luis", address="Calle 2", position="Jefe")

    print(lib, lib.catalog)
    print("Búsqueda Patron:", patron.search(lib.catalog, "cien"))
    print("Búsqueda Librarian:", librarian.search(lib.catalog, "cien"))
    print("Prestado:", acc.borrowed)
    print("OK: multiplicidades, agregación, composición e interfaces verificadas.")
