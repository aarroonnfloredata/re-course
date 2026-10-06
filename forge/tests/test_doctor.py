import pytest

from forge import doctor


@pytest.fixture
def machine(monkeypatch):
    """A fake machine: every tool installed and every command succeeding,
    unless a test says otherwise."""
    state = {"missing": set(), "failing": set(),
             "versions": {"bash": "GNU bash, version 3.2.57(1)-release (arm64-apple-darwin24)"}}

    def which(command):
        return None if command in state["missing"] else f"/usr/bin/{command}"

    def run(command):
        if any(part in state["failing"] for part in command):
            return False, "something went wrong\nerror: could not resolve"
        return True, state["versions"].get(command[0], f"{command[0]} 1.0")

    monkeypatch.setattr(doctor.shutil, "which", which)
    monkeypatch.setattr(doctor, "run", run)
    return state


def test_everything_ready(machine, capsys):
    assert doctor.main() == 0
    out = capsys.readouterr().out
    assert "✓ uv: uv 1.0" in out
    assert "✓ course environment" in out
    assert "✓ bash: GNU bash, version 3.2.57" in out
    assert "✓ bash course environment (ShellCheck)" in out
    assert "Everything is ready." in out


def test_newer_bash_is_a_warning(machine, capsys):
    machine["versions"]["bash"] = "GNU bash, version 5.2.37(1)-release (aarch64-apple-darwin24)"
    assert doctor.main() == 0
    out = capsys.readouterr().out
    assert "! bash: GNU bash, version 5.2.37" in out
    assert "won't catch features that 3.2 lacks" in out
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


def test_broken_bash_course_environment(machine, capsys):
    machine["failing"].add("shellcheck")
    assert doctor.main() == 1
    assert "✗ bash course environment (ShellCheck)" in capsys.readouterr().out
