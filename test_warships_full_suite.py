from __future__ import annotations

import logging
import sqlite3
from typing import Generator, List, Tuple

import pytest

from config import DatabaseConfig, TableSizes

# ------------------------------------ Logging configuration ------------------------------------
# Only essential session-wide events use INFO.
# Per-ship execution logs are DEBUG to avoid clutter in test reports.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


# ------------------------------------ Component field mapping ------------------------------------
COMPONENTS: dict[str, List[str]] = {
    "weapons": ["reload_speed", "rotational_speed", "diameter", "power_volley", "count"],
    "hulls": ["armor", "type", "capacity"],
    "engines": ["power", "type"]
}


# ------------------------------------ Fixtures ----------------------------------------------
@pytest.fixture(scope="session")
def original_db_connection() -> Generator[sqlite3.Connection, None, None]:
    """
    Provides a persistent connection to the original database for comparison.
    Guaranteed to close safely after the entire test session completes.
    """
    connection: sqlite3.Connection = sqlite3.connect(DatabaseConfig.DB_NAME.value)
    logger.info("Connected to original database for test validation.")
    try:
        yield connection
    finally:
        connection.close()
        logger.info("Closed connection to original database.")


@pytest.fixture(scope="session")
def db_component_tables() -> List[str]:
    """Exposes list of component table names for potential test extensions."""
    return list(COMPONENTS.keys())


# ------------------------------------ Component validation tests ------------------------------------
@pytest.mark.parametrize(
    "ship_number, component_table, checked_fields",
    [
        (idx, table, COMPONENTS[table])
        for idx in range(1, TableSizes.SHIPS.value + 1)
        for table in COMPONENTS.keys()
    ]
)
def test_ship_components(
    ship_number: int,
    component_table: str,
    checked_fields: List[str],
    original_db_connection: sqlite3.Connection,
    randomized_database: str
) -> None:
    """
    Validates that randomized database copy meets component randomization test criteria.

    Failure cases:
        1) A component attribute value differs from the original database state.
        2) A ship's FK reference (weapon, hull, or engine) was reassigned to a different component.

    Expected failure output must strictly match the provided Wargaming task format.
    """
    logger.debug(f"--- Running component validation: Ship-{ship_number}, table='{component_table}' ---")

    rand_conn: sqlite3.Connection = sqlite3.connect(randomized_database)
    try:
        orig_cursor = original_db_connection.cursor()
        rand_cursor = rand_conn.cursor()

        # Original FK lookup
        orig_cursor.execute(
            "SELECT weapon, hull, engine FROM ships WHERE ship = ?",
            (f"Ship-{ship_number}",)
        )
        orig_fks: Tuple[str, str, str] | None = orig_cursor.fetchone()
        assert orig_fks is not None, f"Original DB missing row for Ship-{ship_number}"

        active_fk = {
            "weapons": orig_fks[0],
            "hulls": orig_fks[1],
            "engines": orig_fks[2]
        }[component_table]

        # Component values lookup (original)
        pk_column = component_table[:-1]
        orig_cursor.execute(
            f"SELECT {', '.join(checked_fields)} FROM {component_table} WHERE {pk_column} = ?",
            (active_fk,)
        )
        orig_vals: Tuple[int, ...] | None = orig_cursor.fetchone()
        assert orig_vals is not None, f"Original component row missing for {active_fk}"

        # Component values lookup (randomized)
        rand_cursor.execute(
            f"SELECT {', '.join(checked_fields)} FROM {component_table} WHERE {pk_column} = ?",
            (active_fk,)
        )
        rand_vals: Tuple[int, ...] | None = rand_cursor.fetchone()
        assert rand_vals is not None, f"Randomized component row missing for {active_fk}"

        # 1) Field comparison block
        logger.debug("Comparing field values between original and randomized database...")
        for field, expected_val, actual_val in zip(checked_fields, orig_vals, rand_vals):
            if expected_val != actual_val:
                logger.error(
                    f"Component attribute mismatch for {active_fk} ({field}): expected={expected_val}, actual={actual_val}"
                )
                pytest.fail(
                    f"Ship-{ship_number}, {active_fk}\n"
                    f"    {field}: expected {expected_val}, was {actual_val}"
                )

        # 2) FK reassignment detection block
        logger.debug("Checking that ship FK reference was not reassigned...")
        rand_cursor.execute(
            "SELECT weapon, hull, engine FROM ships WHERE ship = ?",
            (f"Ship-{ship_number}", )
        )
        rand_fks: Tuple[str, str, str] | None = rand_cursor.fetchone()
        assert rand_fks is not None, f"Randomized DB missing row for Ship-{ship_number}"

        rand_active_fk = {
            "weapons": rand_fks[0],
            "hulls": rand_fks[1],
            "engines": rand_fks[2]
        }[component_table]

        if active_fk != rand_active_fk:
            logger.error(
                f"FK reference reassigned for Ship-{ship_number}: expected {active_fk}, found {rand_active_fk}"
            )
            pytest.fail(
                f"Ship-{ship_number}, {active_fk}\n"
                f"    expected {active_fk}, was {rand_active_fk}"
            )

        logger.debug(f"Component intact for Ship-{ship_number} ({active_fk})")

    except Exception as ex:
        logger.exception(f"Unexpected failure validating Ship-{ship_number}: {ex}")
        raise

    finally:
        rand_conn.close()
        logger.debug(f"Randomized DB connection closed for Ship-{ship_number}")
