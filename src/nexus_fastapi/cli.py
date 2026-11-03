"""
Command-line interface for Nexus-FastAPI.

Usage
-----
nexus-fastapi                    # creates default project 'my_fastapi_app'
nexus-fastapi create_project my_api       # default scaffold
nexus-fastapi create_project my_api --config config.json  # custom config
"""

from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from typing import Any

from .scaffolds import create_project, DEFAULT_LAYOUT


def _load_config(path: str | None) -> dict[str, Any] | None:
    if not path:
        return None
    p = Path(path).expanduser()
    if not p.is_file():
        sys.exit(f"❌  Config file not found: {p}")
    try:
        return json.loads(p.read_text())
    except json.JSONDecodeError as e:
        sys.exit(f"❌  Invalid JSON in {p}: {e}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nexus-fastapi",
        description="Nexus-FastAPI: scaffold & plug-in framework on top of FastAPI",
    )
    sub = parser.add_subparsers(dest="command", required=False)

    # ── create_project ───────────────────────────────────────────────────
    c = sub.add_parser("create_project", help="Create a new FastAPI project scaffold")
    c.add_argument("project_name", nargs="?", default="my_fastapi_app", 
                  help="Directory name for the new project (default: my_fastapi_app)")
    c.add_argument(
        "--config",
        help="Optional JSON file with project configuration",
    )
    c.set_defaults(func=create_custom_project)
    
    return parser


def create_default_project():
    """Create a project with default settings."""
    create_project(
        root="my_fastapi_app",
        template="default",
        project_name="my_fastapi_app"
    )
    print("🛠️  Project 'my_fastapi_app' created successfully.")
    print("\nTo run the project:")
    print("1. cd my_fastapi_app")
    print("2. pip install -r requirements.txt")
    print("3. uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    print("\nAPI documentation will be available at: http://localhost:8000/docs")


def create_custom_project(args):
    """Create a project with custom settings."""
    config = _load_config(args.config)
    create_project(
        root=args.project_name,
        template="default",
        project_name=args.project_name,
        config=config
    )
    print(f"🛠️  Project '{args.project_name}' created successfully.")
    print("\nTo run the project:")
    print(f"1. cd {args.project_name}")
    print("2. pip install -r requirements.txt")
    print("3. uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    print("\nAPI documentation will be available at: http://localhost:8000/docs")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if getattr(args, "func", None):
        args.func(args)
    else:
        create_default_project()


if __name__ == "__main__":
    main()
