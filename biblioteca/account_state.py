"""«enumeration» AccountState — tipo de dato enumerado del diagrama."""
from enum import Enum


class AccountState(Enum):
    ACTIVE = "Active"
    FROZEN = "Frozen"
    CLOSED = "Closed"
