from __future__ import annotations

"""
Handles creation and population of the Warships SQLite database.
"""

import logging
import random
import sqlite3
from pathlib import Path
from typing import Optional

from config import DatabaseConfig, TableSizes, ValueRange

logger = logging.getLogger(__name__)


class WarshipsDatabase:
    """Manages Warships SQLite database: schema creation, population, cleanup."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path: str = str(Path(db_path or DatabaseConfig.DB_NAME.value).resolve())
        self.connection: sqlite3.Connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.connection.execute("PRAGMA foreign_keys = ON;")

    # ------------------------------------ Context manager ------------------------------------
    def __enter__(self) -> "WarshipsDatabase":
        return self

    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb) -> None:
        self.close()

    # ------------------------------------ Schema creation ------------------------------------
    def create_schema(self) -> None:
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS weapons (
                    weapon TEXT PRIMARY KEY,
                    reload_speed INTEGER,
                    rotational_speed INTEGER,
                    diameter INTEGER,
                    power_volley INTEGER,
                    count INTEGER
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS hulls (
                    hull TEXT PRIMARY KEY,
                    armor INTEGER,
                    type INTEGER,
                    capacity INTEGER
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS engines (
                    engine TEXT PRIMARY KEY,
                    power INTEGER,
                    type INTEGER
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ships (
                    ship TEXT PRIMARY KEY,
                    weapon TEXT,
                    hull TEXT,
                    engine TEXT,
                    FOREIGN KEY (weapon) REFERENCES weapons(weapon),
                    FOREIGN KEY (hull) REFERENCES hulls(hull),
                    FOREIGN KEY (engine) REFERENCES engines(engine)
                );
            """)
            self.connection.commit()
            logger.info("Database schema created successfully.")
        except sqlite3.Error as e:
            logger.error(f"Failed to create schema: {e}")
            raise

    # ------------------------------------ Helper utilities ------------------------------------
    @staticmethod
    def _rand() -> int:
        return random.randint(ValueRange.MIN_VALUE.value, ValueRange.MAX_VALUE.value)

    @staticmethod
    def _name(entity: str, idx: int) -> str:
        return f"{entity}-{idx}"

    # ------------------------------------ Population methods ------------------------------------
    def populate_weapons(self) -> None:
        cursor = self.connection.cursor()
        try:
            for i in range(1, TableSizes.WEAPONS.value + 1):
                name = self._name("Weapon", i)
                values = (self._rand(), self._rand(), self._rand(), self._rand(), self._rand())
                cursor.execute("INSERT OR REPLACE INTO weapons VALUES (?, ?, ?, ?, ?, ?);", (name, *values))
            self.connection.commit()
            logger.info(f"Populated {TableSizes.WEAPONS.value} weapons.")
        except sqlite3.Error as e:
            logger.error(f"Error populating weapons: {e}")
            raise

    def populate_hulls(self) -> None:
        cursor = self.connection.cursor()
        try:
            for i in range(1, TableSizes.HULLS.value + 1):
                name = self._name("Hull", i)
                values = (self._rand(), self._rand(), self._rand())
                cursor.execute("INSERT OR REPLACE INTO hulls VALUES (?, ?, ?, ?);", (name, *values))
            self.connection.commit()
            logger.info(f"Populated {TableSizes.HULLS.value} hulls.")
        except sqlite3.Error as e:
            logger.error(f"Error populating hulls: {e}")
            raise

    def populate_engines(self) -> None:
        cursor = self.connection.cursor()
        try:
            for i in range(1, TableSizes.ENGINES.value + 1):
                name = self._name("Engine", i)
                values = (self._rand(), self._rand())
                cursor.execute("INSERT OR REPLACE INTO engines VALUES (?, ?, ?);", (name, *values))
            self.connection.commit()
            logger.info(f"Populated {TableSizes.ENGINES.value} engines.")
        except sqlite3.Error as e:
            logger.error(f"Error populating engines: {e}")
            raise

    def populate_ships(self) -> None:
        cursor = self.connection.cursor()
        weapon_keys = [f"Weapon-{i}" for i in range(1, TableSizes.WEAPONS.value + 1)]
        hull_keys = [f"Hull-{i}" for i in range(1, TableSizes.HULLS.value + 1)]
        engine_keys = [f"Engine-{i}" for i in range(1, TableSizes.ENGINES.value + 1)]

        try:
            for i in range(1, TableSizes.SHIPS.value + 1):
                name = self._name("Ship", i)
                weapon = random.choice(weapon_keys)
                hull = random.choice(hull_keys)
                engine = random.choice(engine_keys)
                cursor.execute("INSERT OR REPLACE INTO ships VALUES (?, ?, ?, ?);", (name, weapon, hull, engine))
            self.connection.commit()
            logger.info(f"Populated {TableSizes.SHIPS.value} ships.")
        except sqlite3.Error as e:
            logger.error(f"Error populating ships: {e}")
            raise

    def populate_all(self) -> None:
        """Orchestrate full schema creation and table population."""
        self.create_schema()
        self.populate_weapons()
        self.populate_hulls()
        self.populate_engines()
        self.populate_ships()
        logger.info("All tables populated successfully.")

    # ------------------------------------ Cleanup ------------------------------------
    def close(self) -> None:
        if self.connection:
            self.connection.close()
            logger.info(f"Closed database connection to '{self.db_path}'.")
