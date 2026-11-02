from pathlib import Path

import pytest
import yaml

from job_seeker import cli
from job_seeker.profile import ProfileError, load_profile, parse_profile

EXAMPLE = Path(__file__).parent.parent / "profile.example.yaml"


def test_example_profile_loads():
    profile = load_profile(EXAMPLE)
    assert profile.name == "Jane Doe"
    assert profile.experience[0].company == "Example Corp"
    assert profile.projects[0].tech == ["Python"]


def test_missing_required_fields_are_listed():
    with pytest.raises(ProfileError, match="headline, summary"):
        parse_profile({"name": "X", "years_experience": 1, "skills": ["Go"]})


def test_unknown_field_in_entry_is_reported():
    data = yaml.safe_load(EXAMPLE.read_text())
    data["experience"][0]["salary"] = 1
    with pytest.raises(ProfileError, match="experience"):
        parse_profile(data)


def test_missing_file_gives_hint(tmp_path):
    with pytest.raises(ProfileError, match="profile.example.yaml"):
        load_profile(tmp_path / "profile.yaml")


def test_profile_command_prints_summary(capsys):
    assert cli.main(["profile", "--path", str(EXAMPLE)]) == 0
    assert "Jane Doe — Full-stack developer" in capsys.readouterr().out
