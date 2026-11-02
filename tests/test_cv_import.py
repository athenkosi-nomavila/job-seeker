import pytest
import yaml

from job_seeker import cv_import
from job_seeker.profile import parse_profile

CV_TEXT = """\
Jane Doe

   jane@example.com          061 465 1356
   linkedin.com/in/jane-doe   Portfolio

Summary
Backend developer with 3 years of experience
building payment systems.

Skills
Python • Java • Spring
Boot • PostgreSQL

Experience
   Software Developer
   Example Corp
   ●  Built things.

Education
   Example College
"""


def test_draft_profile_extracts_header_summary_and_skills():
    profile, _ = cv_import.draft_profile(CV_TEXT)
    assert profile["name"] == "Jane Doe"
    assert profile["contact"] == {
        "email": "jane@example.com",
        "phone": "061 465 1356",
        "linkedin": "linkedin.com/in/jane-doe",
    }
    assert profile["summary"] == (
        "Backend developer with 3 years of experience building payment systems."
    )
    assert profile["skills"] == ["Python", "Java", "Spring Boot", "PostgreSQL"]


def test_rendered_draft_is_valid_yaml_with_sections_as_comments():
    rendered = cv_import.render_draft(CV_TEXT)
    assert "# Example Corp" in rendered
    assert "# Example College" in rendered
    data = yaml.safe_load(rendered)
    data.update(headline="Backend developer", years_experience=3)
    assert parse_profile(data).name == "Jane Doe"


def test_import_refuses_to_overwrite(tmp_path, monkeypatch):
    monkeypatch.setattr(cv_import, "extract_text", lambda _: CV_TEXT)
    cv = tmp_path / "cv.pdf"
    cv.touch()
    out = tmp_path / "profile.yaml"
    cv_import.import_cv(cv, out)
    with pytest.raises(FileExistsError):
        cv_import.import_cv(cv, out)
    cv_import.import_cv(cv, out, force=True)


def test_import_reports_missing_cv(tmp_path):
    with pytest.raises(FileNotFoundError, match="CV not found"):
        cv_import.import_cv(tmp_path / "nope.pdf", tmp_path / "profile.yaml")
