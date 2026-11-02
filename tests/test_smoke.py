from job_seeker import cli, db


def test_planned_command_prints_phase(capsys):
    assert cli.main(["fetch"]) == 0
    assert "Phase 2" in capsys.readouterr().out


def test_init_db_creates_schema_version(tmp_path):
    conn = db.connect(tmp_path / "data" / "test.db")
    db.init_db(conn)
    db.init_db(conn)  # running twice is safe
    rows = conn.execute("SELECT version FROM schema_version").fetchall()
    assert [r["version"] for r in rows] == [0]
