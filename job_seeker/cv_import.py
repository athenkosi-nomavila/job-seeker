"""Draft a profile from a CV PDF.

This pulls out what can be found reliably (name, contact details, summary and
skills). Experience, projects and education are copied in as comments for you
to turn into entries, because their layout differs too much between CVs to
parse safely. Always review the draft before using it.
"""

import re
from pathlib import Path

import yaml
from pypdf import PdfReader

# Section headings we recognise, mapped to the profile field they belong to.
HEADINGS = {
    "summary": "summary",
    "profile": "summary",
    "about me": "summary",
    "skills": "skills",
    "technical skills": "skills",
    "experience": "experience",
    "work experience": "experience",
    "employment": "experience",
    "projects": "projects",
    "education": "education",
}

EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE = re.compile(r"(?:\+27|0)\d{2}[\s-]?\d{3}[\s-]?\d{4}")
LINKEDIN = re.compile(r"(?:https?://)?(?:www\.)?linkedin\.com/in/[\w-]+")
SKILL_SEPARATORS = re.compile(r"\s*(?:•|·|\||,|;|\n)\s*")


def extract_text(pdf_path: Path) -> str:
    """Read all text from a PDF, keeping the visual layout of lines."""
    reader = PdfReader(pdf_path)
    return "\n".join(page.extract_text(extraction_mode="layout") for page in reader.pages)


def split_sections(text: str) -> tuple[list[str], dict[str, list[str]]]:
    """Split CV text into the header (before any heading) and known sections."""
    header: list[str] = []
    sections: dict[str, list[str]] = {}
    current = None
    for raw in text.splitlines():
        line = raw.strip()
        field = HEADINGS.get(line.lower().rstrip(":"))
        if field:
            current = field
            sections.setdefault(field, [])
        elif current:
            sections[current].append(line)
        else:
            header.append(line)
    return header, sections


def _clean(lines: list[str]) -> list[str]:
    return [line for line in lines if line]


def draft_profile(text: str) -> tuple[dict, dict[str, list[str]]]:
    """Build a draft profile dict from CV text.

    Also returns the CV sections, so callers can show the parts that weren't parsed.
    """
    header, sections = split_sections(text)
    header_text = "\n".join(header)
    name = next(iter(_clean(header)), "")

    contact = {}
    for key, pattern in (("email", EMAIL), ("phone", PHONE), ("linkedin", LINKEDIN)):
        if match := pattern.search(header_text):
            contact[key] = match.group(0)

    skills_text = " ".join(_clean(sections.get("skills", [])))
    skills = [s for s in SKILL_SEPARATORS.split(skills_text) if s]

    return {
        "name": name,
        "headline": "",
        "summary": " ".join(_clean(sections.get("summary", []))),
        "years_experience": 0,
        "contact": contact,
        "skills": skills,
        "experience": [],
        "projects": [],
        "education": [],
    }, sections


def render_draft(text: str) -> str:
    """The draft profile as YAML, with unparsed sections as comments."""
    profile, sections = draft_profile(text)
    out = [
        "# Drafted by `job-seeker profile import`. Review every field.",
        "# Fill in headline and years_experience, and turn the commented",
        "# sections at the bottom into experience, projects and education entries.",
        "",
        yaml.safe_dump(profile, sort_keys=False, allow_unicode=True, width=100),
    ]
    for field in ("experience", "projects", "education"):
        lines = _clean(sections.get(field, []))
        if lines:
            out.append(f"# --- {field} (from your CV) ---")
            out += [f"# {line}" for line in lines]
            out.append("")
    return "\n".join(out)


def import_cv(pdf_path: Path, out_path: Path, force: bool = False) -> None:
    """Write a draft profile for the CV at pdf_path to out_path."""
    if not pdf_path.exists():
        raise FileNotFoundError(f"CV not found at {pdf_path}.")
    if out_path.exists() and not force:
        raise FileExistsError(f"{out_path} already exists. Use --force to overwrite it.")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(render_draft(extract_text(pdf_path)))
