import os
import pytest
from app.db.database import DuckDBManager


@pytest.fixture
def db():
    manager = DuckDBManager.__new__(DuckDBManager)
    manager._instance = None
    manager._conn = None
    manager._schema_info = ""
    manager._row_count = 0
    return manager


def test_not_initialized(db):
    assert not db.is_loaded
    with pytest.raises(RuntimeError, match="not initialized"):
        _ = db.conn


def test_load_and_query(db, tmp_path):
    csv_file = tmp_path / "test.csv"
    csv_file.write_text(
        '"Unique Key","Created Date","Closed Date","Agency","Complaint Type","Borough","Status","Latitude","Longitude"\n'
        '1,"01/01/2020 12:00:00 AM","01/02/2020 12:00:00 AM","NYPD","Noise","MANHATTAN","Closed",40.7,-73.9\n'
        '2,"01/01/2020 01:00:00 AM",,"DOT","Pothole","BROOKLYN","Open",40.6,-73.95\n'
        '3,"01/02/2020 02:00:00 AM","01/02/2020 06:00:00 AM","NYPD","Noise","QUEENS","Closed",40.72,-73.8\n'
    )
    db.load_data(str(csv_file))
    assert db.is_loaded
    assert db.row_count == 3
    assert "service_requests" in db.schema_info

    cols, rows = db.execute_query('SELECT COUNT(*) as cnt FROM service_requests')
    assert cols == ["cnt"]
    assert rows[0][0] == 3


def test_write_operations_blocked(db, tmp_path):
    csv_file = tmp_path / "test.csv"
    csv_file.write_text(
        '"Unique Key","Complaint Type"\n1,"Noise"\n'
    )
    db.load_data(str(csv_file))

    for stmt in ["DROP TABLE service_requests", "DELETE FROM service_requests", "INSERT INTO service_requests VALUES (1)"]:
        with pytest.raises(ValueError, match="Write operations"):
            db.execute_query(stmt)
