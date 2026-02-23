import os
import logging
from app.db.database import db_manager

logger = logging.getLogger(__name__)


def initialize_database(data_path: str) -> None:
    """Load the CSV dataset into DuckDB at application startup."""
    if not os.path.exists(data_path):
        raise FileNotFoundError(
            f"Dataset not found at {data_path}. "
            "Place 311_Service_Requests_from_2010_to_Present.csv in the data directory."
        )

    file_size_mb = os.path.getsize(data_path) / (1024 * 1024)
    logger.info("Found dataset: %.1f MB at %s", file_size_mb, data_path)

    db_manager.load_data(data_path)
    logger.info("Database ready: %d rows loaded", db_manager.row_count)
