from __future__ import annotations

"""
Command-line interface (CLI) for Warships database generation.

This script will automatically create the SQLite database schema and populate all tables with randomized data.
"""

import logging
from pathlib import Path

from warships_database import WarshipsDatabase

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


def main() -> None:
    """CLI entry point: automatically create and populate the database."""
    db_path = str(Path("warships.db").resolve())

    try:
        with WarshipsDatabase(db_path=db_path) as db:
            logging.info("Creating and populating the database...")
            db.populate_all()
            logging.info(f"Database ready at '{db_path}'.")

    except Exception as e:
        logging.exception(f"An error occurred while processing the database: {e}")


if __name__ == "__main__":
    main()
