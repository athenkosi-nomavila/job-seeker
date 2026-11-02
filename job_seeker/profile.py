"""Your candidate profile: the structured version of your CV.

Later phases read this to match jobs (Phase 3) and write tailored CVs and
cover letters (Phase 4). The real file lives in data/profile.yaml, which is
gitignored. See profile.example.yaml for the format.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


class ProfileError(ValueError):
    """The profile file is missing or doesn't match the expected format."""


@dataclass
class Experience:
    title: str
    company: str
    start: str
    end: str = "Present"
    highlights: list[str] = field(default_factory=list)
    tech: list[str] = field(default_factory=list)


@dataclass
class Project:
    name: str
    description: str
    tech: list[str] = field(default_factory=list)


@dataclass
class Education:
    institution: str
    qualification: str
    start: str = ""
    end: str = ""


@dataclass
class Profile:
    name: str
    headline: str
    summary: str
    years_experience: float
    skills: list[str]
    contact: dict[str, str] = field(default_factory=dict)
    experience: list[Experience] = field(default_factory=list)
    projects: list[Project] = field(default_factory=list)
    education: list[Education] = field(default_factory=list)


REQUIRED = ("name", "headline", "summary", "years_experience", "skills")


def parse_profile(data: dict[str, Any]) -> Profile:
    """Build a Profile from parsed YAML, with clear errors for missing fields."""
    if not isinstance(data, dict):
        raise ProfileError("Profile must be a YAML mapping (key: value pairs).")
    missing = [key for key in REQUIRED if not data.get(key)]
    if missing:
        raise ProfileError(f"Profile is missing required fields: {', '.join(missing)}")

    def build(cls, key):
        try:
            return [cls(**item) for item in data.get(key) or []]
        except TypeError as e:
            raise ProfileError(f"Invalid entry under '{key}': {e}") from e

    return Profile(
        name=data["name"],
        headline=data["headline"],
        summary=data["summary"].strip(),
        years_experience=float(data["years_experience"]),
        skills=list(data["skills"]),
        contact=dict(data.get("contact") or {}),
        experience=build(Experience, "experience"),
        projects=build(Project, "projects"),
        education=build(Education, "education"),
    )


def load_profile(path: Path) -> Profile:
    """Read and validate the profile file."""
    if not path.exists():
        raise ProfileError(f"{path} not found. Copy profile.example.yaml to {path} and fill it in.")
    with path.open() as f:
        return parse_profile(yaml.safe_load(f))


def summarise(profile: Profile) -> str:
    """A short, human-readable overview of the profile."""
    lines = [
        f"{profile.name} — {profile.headline}",
        f"{profile.years_experience:g} years of experience",
        f"Skills: {', '.join(profile.skills)}",
        "",
        f"Experience ({len(profile.experience)}):",
    ]
    lines += [f"  - {e.title}, {e.company} ({e.start} – {e.end})" for e in profile.experience]
    lines.append(f"Projects ({len(profile.projects)}):")
    lines += [f"  - {p.name}" for p in profile.projects]
    lines.append(f"Education ({len(profile.education)}):")
    lines += [f"  - {ed.qualification}, {ed.institution}" for ed in profile.education]
    return "\n".join(lines)
