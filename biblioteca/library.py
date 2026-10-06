"""Library — agregación de Account y composición de Catalog."""
from __future__ import annotations
from typing import List, TYPE_CHECKING
from .catalog import Catalog

if TYPE_CHECKING:
    from .account import Account


class Library:
    """Agregación (rombo blanco): 1 <>-- * Account. Composición (rombo negro): posee Catalog."""

    def __init__(self, name: str, address: str):
        self.name = name
        self.address = address
        self._accounts: List[Account] = []
        # Composición: la Library crea su Catalog (ciclo de vida dependiente)
        self._catalog = Catalog(library=self)

    @property
    def accounts(self) -> List[Account]:
        return list(self._accounts)

    @property
    def catalog(self) -> Catalog:
        return self._catalog

    def add_account(self, account: Account) -> None:
        """Agregación: vincula una cuenta que ya existe fuera."""
        if account not in self._accounts:
            self._accounts.append(account)

    def remove_account(self, account: Account) -> None:
        """Al quitarla, el objeto Account sigue existiendo (no es composición)."""
        if account in self._accounts:
            self._accounts.remove(account)

    def __repr__(self) -> str:
        return f"Library(name={self.name!r}, accounts={len(self._accounts)})"
