from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SEED_SCRIPT = REPO_ROOT / "scripts" / "new-brain" / "seed-brain.sh"


def _setup_fake_repo(tmp_path: Path) -> Path:
    """Build a minimal repo skeleton with _brain_template/ and seed-brain.sh."""
    template = tmp_path / "_brain_template"
    template.mkdir()
    (template / "Vault").mkdir()
    (template / "Vault" / "README.md").write_text("# Template\n", encoding="utf-8")
    (template / "_meta").mkdir()
    (template / "_meta" / "taxonomy.md").write_text("# Taxonomy\n", encoding="utf-8")

    scripts_new_brain = tmp_path / "scripts" / "new-brain"
    scripts_new_brain.mkdir(parents=True)
    shutil.copy(SEED_SCRIPT, scripts_new_brain / "seed-brain.sh")
    (scripts_new_brain / "seed-brain.sh").chmod(0o755)

    return tmp_path


def _run(seed: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(seed), *args],
        capture_output=True,
        text=True,
    )


def test_general_brain_lands_at_repo_root(tmp_path):
    repo = _setup_fake_repo(tmp_path)
    seed = repo / "scripts" / "new-brain" / "seed-brain.sh"

    result = _run(seed, "TestGeneral")

    assert result.returncode == 0, result.stderr
    assert (repo / "TestGeneral" / "Vault" / "README.md").exists()
    assert not (repo / ".Project Context" / "TestGeneral").exists()


def test_project_context_flag_lands_under_project_context(tmp_path):
    repo = _setup_fake_repo(tmp_path)
    seed = repo / "scripts" / "new-brain" / "seed-brain.sh"

    result = _run(seed, "TestProject", "--project-context")

    assert result.returncode == 0, result.stderr
    assert (repo / ".Project Context" / "TestProject" / "Vault" / "README.md").exists()
    assert not (repo / "TestProject").exists()


def test_force_with_project_context_reseeds(tmp_path):
    repo = _setup_fake_repo(tmp_path)
    seed = repo / "scripts" / "new-brain" / "seed-brain.sh"

    _run(seed, "TestProject", "--project-context")
    # Mark the existing folder so we can detect the rebuild.
    marker = repo / ".Project Context" / "TestProject" / "marker.txt"
    marker.write_text("before", encoding="utf-8")

    result = _run(seed, "TestProject", "--project-context", "--force")

    assert result.returncode == 0, result.stderr
    assert (repo / ".Project Context" / "TestProject" / "Vault" / "README.md").exists()
    assert not marker.exists(), "--force should have removed the existing folder before re-seeding"


def test_refuse_existing_target_without_force(tmp_path):
    repo = _setup_fake_repo(tmp_path)
    seed = repo / "scripts" / "new-brain" / "seed-brain.sh"
    (repo / "TestExisting").mkdir()

    result = _run(seed, "TestExisting")

    assert result.returncode != 0
    assert "already exists" in result.stderr.lower()


def test_refuse_unknown_flag(tmp_path):
    repo = _setup_fake_repo(tmp_path)
    seed = repo / "scripts" / "new-brain" / "seed-brain.sh"

    result = _run(seed, "TestFoo", "--bogus")

    assert result.returncode != 0
    assert "unknown flag" in result.stderr.lower()


def test_refuse_path_traversal(tmp_path):
    repo = _setup_fake_repo(tmp_path)
    seed = repo / "scripts" / "new-brain" / "seed-brain.sh"

    result = _run(seed, "../escape")

    assert result.returncode != 0
    assert "must not contain" in result.stderr.lower()
