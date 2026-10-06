import pytest

from forge import doctor


@pytest.fixture
def machine(monkeypatch):
    """A fake machine: every tool installed and every command succeeding,
    unless a test says otherwise."""
    state = {"missing": set(), "failing": set()}

    def which(command):
        return None if command in state["missing"] else f"/usr/bin/{command}"

    def run(command):
        if any(part in state["failing"] for part in command):
            return False, "something went wrong\nerror: could not resolve"
        return True, f"{command[0]} 1.0"

    monkeypatch.setattr(doctor.shutil, "which", which)
    monkeypatch.setattr(doctor, "run", run)
    return state


def test_everything_ready(machine, capsys):
    assert doctor.main() == 0
    out = capsys.readouterr().out
    assert "✓ uv: uv 1.0" in out
    assert "✓ course environment" in out
    assert "Everything is ready." in out


def test_missing_tool(machine, capsys):
    machine["missing"].add("claude")
    assert doctor.main() == 1
    out = capsys.readouterr().out
    assert "✗ Claude Code not found. Install it:" in out
    assert "1 problem(s) to fix." in out


def test_without_uv_environments_are_not_checked(machine, capsys):
    machine["missing"].add("uv")
    assert doctor.main() == 1
    out = capsys.readouterr().out
    assert "✗ uv not found" in out
    assert "✗ environments not checked: they need uv" in out


def test_broken_course_environment(machine, capsys):
    machine["failing"].add("import learn.authoring, pytest")
    assert doctor.main() == 1
    out = capsys.readouterr().out
    assert "✗ course environment" in out
    assert "error: could not resolve" in out
