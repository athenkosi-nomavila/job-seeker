"""The `job-seeker` command. Each subcommand maps to one phase of the roadmap."""

import argparse
from pathlib import Path

from pypdf.errors import PdfReadError

from job_seeker import __version__, db
from job_seeker.cv_import import import_cv
from job_seeker.profile import DEFAULT_PROFILE, ProfileError, load_profile, summarise

# Subcommands that later phases will implement: name -> (phase, description)
PLANNED = {
    "fetch": (2, "Fetch new job listings from your sources"),
    "match": (3, "Score jobs against your profile and show a shortlist"),
    "tailor": (4, "Write a tailored CV and cover letter for a job"),
    "track": (5, "Show and update your applications"),
    "apply": (6, "Pre-fill an application for you to review and submit"),
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="job-seeker", description=__doc__)
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="Create the local database in data/")
    profile = sub.add_parser("profile", help="Check your profile and show a summary")
    profile.add_argument("--path", type=Path, default=DEFAULT_PROFILE)
    profile_sub = profile.add_subparsers(dest="profile_command")
    cv_import = profile_sub.add_parser("import", help="Draft a profile from a CV PDF")
    cv_import.add_argument("cv", type=Path, help="Path to your CV, e.g. data/cv.pdf")
    cv_import.add_argument("--force", action="store_true", help="Overwrite an existing profile")
    for name, (phase, description) in PLANNED.items():
        sub.add_parser(name, help=f"{description} (coming in Phase {phase})")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "init":
        with db.connect() as conn:
            db.init_db(conn)
        print(f"Database ready at {db.DEFAULT_DB}")
        return 0

    if args.command == "profile" and args.profile_command == "import":
        try:
            import_cv(args.cv, args.path, force=args.force)
        except (FileNotFoundError, FileExistsError, PdfReadError) as e:
            print(f"Error: {e}")
            return 1
        print(f"Draft profile written to {args.path}. Review it, then run `job-seeker profile`.")
        return 0

    if args.command == "profile":
        try:
            print(summarise(load_profile(args.path)))
        except ProfileError as e:
            print(f"Error: {e}")
            return 1
        return 0

    phase, _ = PLANNED[args.command]
    print(f"'{args.command}' isn't built yet. It arrives in Phase {phase}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
