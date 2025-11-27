from __future__ import annotations

"""
Command-line interface (CLI) for Warships database generation.

This script will automatically create the SQLite database schema and populate all tables with randomized data.
"""

from pathlib import Path

from warships_database import WarshipsDatabase


def main() -> None:
    """CLI entry point: automatically create and populate the database."""
    db_path = str(Path("warships.db").resolve())

    with WarshipsDatabase(db_path=db_path) as db:
        print("Creating and populating the database...")
        db.populate_all()
        print(f"Database ready at '{db_path}'.")


if __name__ == "__main__":
    main()
