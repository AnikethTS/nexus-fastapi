from src.nexus_fastapi.scaffolds import create_project
from pathlib import Path
def test_scaffold(tmp_path):
    create_project(tmp_path / "demo")
    assert (tmp_path / "demo/app").exists()
