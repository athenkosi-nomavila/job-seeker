"""The `job-seeker` command. Each subcommand maps to one phase of the roadmap.

To add a command: write a `cmd_<name>(args, settings)` function and register it
in `build_parser` with `set_defaults(handler=...)`.
"""

import argparse
from functools import partial
from pathlib import Path

from pypdf.errors import PdfReadError

from job_seeker import __version__, db
from job_seeker.config import Settings, load_settings
from job_seeker.cv_import import import_cv
from job_seeker.profile import ProfileError, load_profile, summarise

# Errors caused by the user's files or input. They're printed as a message, not a traceback.
USER_ERRORS = (ProfileError, FileNotFoundError, FileExistsError, PdfReadError)

# Subcommands that later phases will implement: name -> (phase, description)
PLANNED = {
    "fetch": (2, "Fetch new job listings from your sources"),
    "match": (3, "Score jobs against your profile and show a shortlist"),
    "tailor": (4, "Write a tailored CV and cover letter for a job"),
    "track": (5, "Show and update your applications"),
    "apply": (6, "Pre-fill an application for you to review and submit"),
}


def cmd_init(args: argparse.Namespace, settings: Settings) -> None:
    with db.connect(settings.db_path) as conn:
        db.init_db(conn)
    print(f"Database ready at {settings.db_path}")


def cmd_profile(args: argparse.Namespace, settings: Settings) -> None:
    print(summarise(load_profile(args.path or settings.profile_path)))


def cmd_profile_import(args: argparse.Namespace, settings: Settings) -> None:
    out = args.path or settings.profile_path
    import_cv(args.cv, out, force=args.force)
    print(f"Draft profile written to {out}. Review it, then run `job-seeker profile`.")


def cmd_planned(args: argparse.Namespace, settings: Settings, phase: int) -> None:
    print(f"'{args.command}' isn't built yet. It arrives in Phase {phase}.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="job-seeker", description=__doc__)
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="Create the local database").set_defaults(handler=cmd_init)

    profile = sub.add_parser("profile", help="Check your profile and show a summary")
    profile.add_argument("--path", type=Path, help="Profile file (default: data/profile.yaml)")
    profile.set_defaults(handler=cmd_profile)
    cv_import = profile.add_subparsers().add_parser("import", help="Draft a profile from a CV PDF")
    cv_import.add_argument("cv", type=Path, help="Path to your CV, e.g. data/cv.pdf")
    cv_import.add_argument("--force", action="store_true", help="Overwrite an existing profile")
    cv_import.set_defaults(handler=cmd_profile_import)

    for name, (phase, description) in PLANNED.items():
        planned = sub.add_parser(name, help=f"{description} (coming in Phase {phase})")
        planned.set_defaults(handler=partial(cmd_planned, phase=phase))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        args.handler(args, load_settings())
    except USER_ERRORS as e:
        print(f"Error: {e}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
