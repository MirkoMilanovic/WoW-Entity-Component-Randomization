from __future__ import annotations

import logging
import random
import shutil
from pathlib import Path
from typing import List

import pytest
from _pytest.tmpdir import TempPathFactory

from config import DatabaseConfig, ValueRange
from warships_database import WarshipsDatabase

# ------------------------------------ Logger setup ------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


# ------------------------------------ Helper functions ------------------------------------
def ensure_database_exists() -> str:
    """
    Ensure the original database exists and is populated.

    Returns:
        str: Absolute path to the original database.

    Raises:
        Exception: If database creation or population fails.
    """
    db_path = Path(DatabaseConfig.DB_NAME.value).resolve()
    try:
        with WarshipsDatabase(str(db_path)) as db:
            db.create_schema()
            cursor = db.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM ships")
            if cursor.fetchone()[0] == 0:
                logger.info("Populating original database...")
                db.populate_all()
                logger.info("Original database populated successfully.")
            else:
                logger.info("Original database already populated.")
    except Exception as e:
        logger.error(f"Failed to ensure original database exists: {e}")
        raise
    return str(db_path)


def randomize_table(
    db_instance: WarshipsDatabase,
    table_name: str,
    params: List[str],
    key_column: str
) -> None:
    """
    Randomize one integer parameter per row for a given table.

    Each row will have **one** randomly selected column from `params`
    set to a random integer between ValueRange.MIN_VALUE and ValueRange.MAX_VALUE.

    Args:
        db_instance (WarshipsDatabase): Open database connection.
        table_name (str): Name of the table to randomize.
        params (List[str]): List of column names to choose from.
        key_column (str): Primary key column of the table.

    Raises:
        Exception: If database access or update fails.
    """
    try:
        cursor = db_instance.connection.cursor()
        cursor.execute(f"SELECT {key_column} FROM {table_name}")
        row_keys = [row[0] for row in cursor.fetchall()]

        for component_key in row_keys:
            column_name = random.choice(params)
            random_value = random.randint(ValueRange.MIN_VALUE.value, ValueRange.MAX_VALUE.value)
            cursor.execute(
                f"UPDATE {table_name} SET {column_name} = ? WHERE {key_column} = ?",
                (random_value, component_key)
            )

        db_instance.connection.commit()
        logger.info(f"Randomized table '{table_name}' successfully ({len(row_keys)} rows updated).")

    except Exception as e:
        logger.error(f"Failed to randomize table '{table_name}': {e}")
        raise


# ------------------------------------ Pytest fixture ------------------------------------
@pytest.fixture(scope="session")
def randomized_database(tmp_path_factory: TempPathFactory) -> str:
    """
    Session-scoped fixture: creates a randomized copy of the database.

    Returns:
        str: Absolute path to the randomized database.

    Raises:
        Exception: If database copy or randomization fails.
    """
    original_db = ensure_database_exists()

    tmp_db_folder = tmp_path_factory.mktemp("data")
    tmp_db_path = tmp_db_folder / "warships_randomized.db"

    try:
        shutil.copy(original_db, tmp_db_path)
        logger.info(f"Copied original database to temporary path: {tmp_db_path}")

        # Randomize each component table
        with WarshipsDatabase(str(tmp_db_path)) as db:
            randomize_table(
                db,
                "weapons",
                ["reload_speed", "rotational_speed", "diameter", "power_volley", "count"],
                "weapon"
            )
            randomize_table(db, "hulls", ["armor", "type", "capacity"], "hull")
            randomize_table(db, "engines", ["power", "type"], "engine")

        logger.info("Randomized database ready for tests.")

    except Exception as e:
        logger.error(f"Failed to create randomized database: {e}")
        raise

    return str(tmp_db_path)
