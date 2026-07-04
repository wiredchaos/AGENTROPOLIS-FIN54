from __future__ import annotations

import logging
import os
import sqlite3
from typing import Any

from fin54.utils.config import CACHE_PATH

logger = logging.getLogger(__name__)

try:
    import duckdb  # type: ignore
except Exception:  # pragma: no cover
    duckdb = None


class Cache:
    def __init__(self, path: str = CACHE_PATH):
        self.path = path
        self.backend = "duckdb" if duckdb is not None else "sqlite"
        if path != ":memory:":
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        if duckdb is not None:
            self.conn = duckdb.connect(path)
        else:
            logger.warning("duckdb unavailable; using sqlite in-memory fallback")
            self.conn = sqlite3.connect(":memory:")
            self.conn.row_factory = sqlite3.Row

    def _column_type(self, value: Any) -> str:
        if isinstance(value, bool):
            return "BOOLEAN"
        if isinstance(value, int) and not isinstance(value, bool):
            return "BIGINT"
        if isinstance(value, float):
            return "DOUBLE"
        return "VARCHAR"

    def _ensure_table(self, table: str, rows: list[dict]) -> list[str]:
        columns = list(rows[0].keys())
        definitions = []
        for column in columns:
            sample = next((row.get(column) for row in rows if row.get(column) is not None), None)
            definitions.append(f'"{column}" {self._column_type(sample)}')
        primary_keys = [col for col in columns if col == "id"] or [col for col in columns if col.endswith("_id")]
        if not primary_keys:
            primary_keys = columns
        pk_sql = ", PRIMARY KEY ({})".format(", ".join(f'"{col}"' for col in primary_keys))
        sql = f'CREATE TABLE IF NOT EXISTS "{table}" ({", ".join(definitions)}{pk_sql})'
        self.conn.execute(sql)
        return columns

    def store(self, table: str, data: list[dict]) -> None:
        if not data:
            return
        columns = self._ensure_table(table, data)
        placeholders = ", ".join(["?"] * len(columns))
        column_sql = ", ".join(f'"{col}"' for col in columns)
        sql = f'INSERT OR REPLACE INTO "{table}" ({column_sql}) VALUES ({placeholders})'
        values = [[row.get(column) for column in columns] for row in data]
        self.conn.executemany(sql, values)

    def query(self, sql: str, params: list[Any] | tuple[Any, ...] | None = None) -> list[dict]:
        params = params or []
        cursor = self.conn.execute(sql, params)
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        rows = cursor.fetchall()
        output = []
        for row in rows:
            if isinstance(row, sqlite3.Row):
                output.append(dict(row))
            else:
                output.append(dict(zip(columns, row)))
        return output

    def close(self) -> None:
        self.conn.close()
