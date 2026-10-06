"""Patron — asociación 'account' + dependencia «use» a Search."""
from __future__ import annotations
from typing import List, TYPE_CHECKING
from .search import Search

if TYPE_CHECKING:
    from .account import Account
    from .book_item import BookItem


class Patron:
    def __init__(self, name: str, address: str, account: Account):
        self.name = name
        self.address = address
        self.account = account
        account.patron = self

    def search(self, service: Search, title: str) -> List[BookItem]:
        """«use»: solo conoce la interfaz Search, no el Catalog concreto."""
        return service.search_by_title(title)

    def __repr__(self) -> str:
        return f"Patron(name={self.name!r})"
