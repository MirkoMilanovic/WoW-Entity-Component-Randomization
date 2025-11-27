import sqlite3

import pytest

from config import DatabaseConfig, TableSizes

COMPONENTS = {
    "weapons": ["reload_speed", "rotational_speed", "diameter", "power_volley", "count"],
    "hulls": ["armor", "type", "capacity"],
    "engines": ["power", "type"]
}


@pytest.fixture(scope="session")
def original_db_connection():
    conn = sqlite3.connect(DatabaseConfig.DB_NAME.value)
    yield conn
    conn.close()


@pytest.mark.parametrize(
    "ship_id, component, fields",
    [
        (i, table, COMPONENTS[table])
        for i in range(1, TableSizes.SHIPS.value + 1)
        for table in COMPONENTS.keys()
    ]
)
def test_basic_component_check(ship_id, component, fields, original_db_connection, randomized_database):
    """Early version of component comparison test."""
    orig_conn = original_db_connection
    rand_conn = sqlite3.connect(randomized_database)

    try:
        orig_cur = orig_conn.cursor()
        rand_cur = rand_conn.cursor()

        # FK lookup
        orig_cur.execute("SELECT weapon, hull, engine FROM ships WHERE ship = ?", (f"Ship-{ship_id}",))
        orig_fks = orig_cur.fetchone()

        fk = {
            "weapons": orig_fks[0],
            "hulls": orig_fks[1],
            "engines": orig_fks[2]
        }[component]

        # original values
        orig_cur.execute(f"SELECT {', '.join(fields)} FROM {component} WHERE {component[:-1]} = ?", (fk,))
        orig_vals = orig_cur.fetchone()

        # randomized values
        rand_cur.execute(f"SELECT {', '.join(fields)} FROM {component} WHERE {component[:-1]} = ?", (fk,))
        rand_vals = rand_cur.fetchone()

        # simple comparison
        assert orig_vals is not None
        assert rand_vals is not None

    finally:
        rand_conn.close()
