from pathlib import Path

from job_seeker.config import Settings, load_settings


def test_defaults_without_config_file(tmp_path):
    settings = load_settings(tmp_path / "config.yaml")
    assert settings == Settings()
    assert settings.profile_path == Path("data/profile.yaml")


def test_data_dir_from_config_moves_every_path(tmp_path):
    config = tmp_path / "config.yaml"
    config.write_text("paths:\n  data_dir: elsewhere\n")
    settings = load_settings(config)
    assert settings.profile_path == Path("elsewhere/profile.yaml")
    assert settings.db_path == Path("elsewhere/job_seeker.db")
