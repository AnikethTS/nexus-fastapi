import json
from pathlib import Path

from nexus_fastapi.scaffolds import create_project

SAMPLE = Path(__file__).resolve().parent.parent / "sample_config.json"


def test_scaffold_default(tmp_path):
    root = create_project(tmp_path / "demo", project_name="demo")
    assert root == (tmp_path / "demo").resolve()
    for rel in ("apps", "core/config", "core/database", "core/security", "tests", "main.py", "run.py"):
        assert (root / rel).exists(), rel


def test_scaffold_respects_root(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    create_project(tmp_path / "elsewhere", project_name="service")
    assert not (tmp_path / "service").exists()


def test_scaffold_from_config(tmp_path):
    config = json.loads(SAMPLE.read_text())
    root = create_project(tmp_path / "cfg", project_name="cfg", config=config)
    for app in ("users", "products"):
        for f in ("models.py", "schemas.py", "crud.py", "routes.py"):
            assert (root / "apps" / app / f).exists(), (app, f)
    for py in root.rglob("*.py"):
        compile(py.read_text(), str(py), "exec")
