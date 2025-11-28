from __future__ import annotations

"""
Basic configuration parameters used by the Warships database.
"""

from enum import Enum


class DatabaseConfig(Enum):
    """Database-level configuration settings."""
    DB_NAME = "warships.db"


class TableSizes(Enum):
    """Required number of records per entity type."""
    SHIPS = 200
    WEAPONS = 20
    HULLS = 5
    ENGINES = 6


class ValueRange(Enum):
    """Defines allowed integer range for generated component attributes."""
    MIN_VALUE = 1
    MAX_VALUE = 20
