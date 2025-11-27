import random
import sqlite3
from pathlib import Path
from typing import Optional

DB_NAME = "warships.db"

SHIPS = 200
WEAPONS = 20
HULLS = 5
ENGINES = 6

MIN_VALUE = 1
MAX_VALUE = 20


class WarshipsDatabase:
    """Handles creation and population of a simple Warships SQLite database."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = str(Path(db_path or DB_NAME).resolve())
        self.connection = sqlite3.connect(self.db_path)
        self.connection.execute("PRAGMA foreign_keys = ON;")

    def create_schema(self) -> None:
        cursor = self.connection.cursor()

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
                engine TEXT
            );
        """)

        self.connection.commit()

    @staticmethod
    def _rand() -> int:
        return random.randint(MIN_VALUE, MAX_VALUE)

    @staticmethod
    def _name(entity: str, idx: int) -> str:
        return f"{entity}-{idx}"

    def populate_weapons(self) -> None:
        cursor = self.connection.cursor()
        for i in range(1, WEAPONS + 1):
            name = self._name("Weapon", i)
            values = (self._rand(), self._rand(), self._rand(), self._rand(), self._rand())
            cursor.execute("INSERT INTO weapons VALUES (?, ?, ?, ?, ?, ?)", (name, *values))
        self.connection.commit()

    def populate_hulls(self) -> None:
        cursor = self.connection.cursor()
        for i in range(1, HULLS + 1):
            name = self._name("Hull", i)
            values = (self._rand(), self._rand(), self._rand())
            cursor.execute("INSERT INTO hulls VALUES (?, ?, ?, ?)", (name, *values))
        self.connection.commit()

    def populate_engines(self) -> None:
        cursor = self.connection.cursor()
        for i in range(1, ENGINES + 1):
            name = self._name("Engine", i)
            values = (self._rand(), self._rand())
            cursor.execute("INSERT INTO engines VALUES (?, ?, ?)", (name, *values))
        self.connection.commit()

    def populate_ships(self) -> None:
        cursor = self.connection.cursor()

        for i in range(1, SHIPS + 1):
            name = self._name("Ship", i)
            weapon = self._name("Weapon", random.randint(1, WEAPONS))
            hull = self._name("Hull", random.randint(1, HULLS))
            engine = self._name("Engine", random.randint(1, ENGINES))

            cursor.execute("INSERT INTO ships VALUES (?, ?, ?, ?)", (name, weapon, hull, engine))

        self.connection.commit()

    def populate_all(self) -> None:
        self.create_schema()
        self.populate_weapons()
        self.populate_hulls()
        self.populate_engines()
        self.populate_ships()


if __name__ == "__main__":
    print("WARSHIPS DB SCRIPT STARTED")
    db = WarshipsDatabase()
    print(f"Creating and populating database: {db.db_path}")
    db.populate_all()
    print("Database created successfully.")
