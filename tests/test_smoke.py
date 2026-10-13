import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def test_repo_has_readme():
    assert (REPO / "README.md").exists()


def test_repo_has_gitignore():
    assert (REPO / ".gitignore").exists()


def test_env_example_present():
    assert (REPO / ".env.example").exists()


def test_no_sensor_data_tracked():
    tracked = subprocess.run(
        ["git", "ls-files", "data"],
        cwd=REPO, capture_output=True, text=True, check=True,
    ).stdout.splitlines()
    assert all(p.endswith(".gitkeep") for p in tracked), f"Artefactos de datos trackeados: {tracked}"


def test_app_imports():
    import sys

    sys.path.insert(0, str(REPO))
    try:
        mod = __import__("app")
        assert hasattr(mod, "app")
    finally:
        sys.path.pop(0)
        sys.modules.pop("app", None)