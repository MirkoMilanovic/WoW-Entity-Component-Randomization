import random
import shutil
from pathlib import Path

import pytest

from config import DatabaseConfig, ValueRange
from warships_database import WarshipsDatabase


def ensure_database_exists() -> str:
    """Ensure the original database exists and is populated."""
    db_path = Path(DatabaseConfig.DB_NAME.value).resolve()
    with WarshipsDatabase(str(db_path)) as db:
        db.create_schema()
        cursor = db.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM ships")
        if cursor.fetchone()[0] == 0:
            db.populate_all()
    return str(db_path)


def randomize_table(db, table_name, params, key_column):
    """Simple randomizer for early testing."""
    cursor = db.connection.cursor()
    cursor.execute(f"SELECT {key_column} FROM {table_name}")
    keys = [row[0] for row in cursor.fetchall()]

    for key in keys:
        param = random.choice(params)
        value = random.randint(ValueRange.MIN_VALUE.value, ValueRange.MAX_VALUE.value)
        cursor.execute(
            f"UPDATE {table_name} SET {param} = ? WHERE {key_column} = ?",
            (value, key)
        )

    db.connection.commit()


@pytest.fixture(scope="session")
def randomized_database(tmp_path_factory):
    """Create temporary randomized DB for tests."""
    original_db = ensure_database_exists()

    tmp_dir = tmp_path_factory.mktemp("data")
    tmp_db = tmp_dir / "warships_randomized.db"
    shutil.copy(original_db, tmp_db)

    with WarshipsDatabase(str(tmp_db)) as db:
        randomize_table(db, "weapons",
                        ["reload_speed", "rotational_speed", "diameter", "power_volley", "count"],
                        "weapon")
        randomize_table(db, "hulls", ["armor", "type", "capacity"], "hull")
        randomize_table(db, "engines", ["power", "type"], "engine")

    return str(tmp_db)
