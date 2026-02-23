import logging
import duckdb

logger = logging.getLogger(__name__)


class DuckDBManager:
    """Singleton manager for the DuckDB in-memory database."""

    _instance: "DuckDBManager | None" = None
    _conn: duckdb.DuckDBPyConnection | None = None
    _schema_info: str = ""
    _row_count: int = 0

    def __new__(cls) -> "DuckDBManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def conn(self) -> duckdb.DuckDBPyConnection:
        if self._conn is None:
            raise RuntimeError("Database not initialized. Call load_data() first.")
        return self._conn

    @property
    def schema_info(self) -> str:
        return self._schema_info

    @property
    def row_count(self) -> int:
        return self._row_count

    @property
    def is_loaded(self) -> bool:
        return self._conn is not None and self._row_count > 0

    def load_data(self, csv_path: str) -> None:
        logger.info("Initializing DuckDB and loading CSV: %s", csv_path)
        self._conn = duckdb.connect(":memory:")

        csv_path_escaped = csv_path.replace("'", "''")
        self._conn.execute(f"""
            CREATE TABLE service_requests AS
            SELECT * FROM read_csv_auto(
                '{csv_path_escaped}',
                header=true,
                sample_size=10000,
                ignore_errors=true,
                nullstr=['N/A', 'Unspecified', '']
            )
        """)

        self._add_resolution_hours()

        count_result = self._conn.execute(
            "SELECT COUNT(*) FROM service_requests"
        ).fetchone()
        self._row_count = count_result[0] if count_result else 0

        self._schema_info = self._build_schema_info()

        logger.info(
            "DuckDB loaded: %d rows from service_requests", self._row_count
        )

    def _add_resolution_hours(self) -> None:
        """Compute resolution_hours if both date columns exist."""
        columns = self._conn.execute("DESCRIBE service_requests").fetchall()
        col_names = [c[0] for c in columns]

        if "Created Date" not in col_names or "Closed Date" not in col_names:
            return

        col_types = {c[0]: c[1].upper() for c in columns}
        created_type = col_types.get("Created Date", "")
        closed_type = col_types.get("Closed Date", "")

        self._conn.execute("""
            ALTER TABLE service_requests ADD COLUMN IF NOT EXISTS resolution_hours DOUBLE
        """)

        if "TIMESTAMP" in created_type or "DATE" in created_type:
            self._conn.execute("""
                UPDATE service_requests
                SET resolution_hours = CASE
                    WHEN "Closed Date" IS NOT NULL AND "Created Date" IS NOT NULL
                    THEN EXTRACT(EPOCH FROM ("Closed Date" - "Created Date")) / 3600.0
                    ELSE NULL
                END
            """)
        else:
            self._conn.execute("""
                UPDATE service_requests
                SET resolution_hours = CASE
                    WHEN "Closed Date" IS NOT NULL AND "Created Date" IS NOT NULL
                    THEN EXTRACT(EPOCH FROM (
                        TRY_STRPTIME("Closed Date", '%m/%d/%Y %I:%M:%S %p') -
                        TRY_STRPTIME("Created Date", '%m/%d/%Y %I:%M:%S %p')
                    )) / 3600.0
                    ELSE NULL
                END
            """)

    def _build_schema_info(self) -> str:
        columns = self._conn.execute(
            "DESCRIBE service_requests"
        ).fetchall()

        lines = ["Table: service_requests", f"Total rows: {self._row_count}", ""]
        lines.append("Columns:")
        for col_name, col_type, *_ in columns:
            sample = self._get_sample_values(col_name)
            lines.append(f"  - \"{col_name}\" ({col_type}): {sample}")

        return "\n".join(lines)

    def _get_sample_values(self, col_name: str) -> str:
        try:
            result = self._conn.execute(f"""
                SELECT DISTINCT "{col_name}"
                FROM service_requests
                WHERE "{col_name}" IS NOT NULL
                LIMIT 5
            """).fetchall()
            values = [str(r[0]) for r in result]
            if values:
                return "e.g. " + ", ".join(values[:5])
            return "all NULL"
        except Exception:
            return "unable to sample"

    def execute_query(self, sql: str) -> tuple[list[str], list[tuple]]:
        """Execute a read-only SQL query and return (column_names, rows)."""
        forbidden = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "TRUNCATE"]
        sql_upper = sql.strip().upper()
        for keyword in forbidden:
            if sql_upper.startswith(keyword):
                raise ValueError(f"Write operations are not allowed: {keyword}")

        result = self._conn.execute(sql)
        columns = [desc[0] for desc in result.description]
        rows = result.fetchall()
        return columns, rows

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None
            logger.info("DuckDB connection closed")


db_manager = DuckDBManager()
