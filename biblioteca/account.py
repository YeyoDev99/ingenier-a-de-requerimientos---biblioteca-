"""«entity» Account — borrowed 0..12, reserved 0..3, «use» AccountState."""
from __future__ import annotations
from datetime import date
from typing import List, Optional, TYPE_CHECKING
from .account_state import AccountState

if TYPE_CHECKING:
    from .book_item import BookItem
    from .patron import Patron


class Account:
    MAX_BORROWED = 12
    MAX_RESERVED = 3

    def __init__(
        self,
        number: str,
        opened: date,
        state: AccountState = AccountState.ACTIVE,
        history: Optional[List[str]] = None,
    ):
        self.number = number  # {id}
        self.history: List[str] = history or []
        self.opened = opened
        self.state = state  # dependencia «use» a la enumeración
        self._borrowed: List[BookItem] = []
        self._reserved: List[BookItem] = []
        self.patron: Optional[Patron] = None

    @property
    def borrowed(self) -> List[BookItem]:
        return list(self._borrowed)

    @property
    def reserved(self) -> List[BookItem]:
        return list(self._reserved)

    def _check_open(self) -> None:
        if self.state == AccountState.CLOSED:
            raise ValueError(f"Account {self.number} está Closed.")
        if self.state == AccountState.FROZEN:
            raise ValueError(f"Account {self.number} está Frozen.")

    def borrow(self, item: BookItem) -> None:
        self._check_open()
        if item.is_reference_only:
            raise ValueError("Ejemplar de referencia no se presta.")
        if item.borrowed_by is not None:
            raise ValueError("Ya está prestado.")
        if len(self._borrowed) >= self.MAX_BORROWED:
            raise ValueError("Máximo 12 prestados (0..12).")
        self._borrowed.append(item)
        item.borrowed_by = self
        self.history.append(f"borrowed {item.barcode}")

    def reserve(self, item: BookItem) -> None:
        self._check_open()
        if len(self._reserved) >= self.MAX_RESERVED:
            raise ValueError("Máximo 3 reservados (0..3).")
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
