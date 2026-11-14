"""Regression tests for uninstall.sh.

The agent files live under bughunter/agents/ in this layout, but uninstall.sh
globbed $SCRIPT_DIR/agents/*.md. The glob matched nothing, so every agent
stayed installed after an uninstall — the same class of bug install.sh had.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
UNINSTALL = REPO / "uninstall.sh"
BASH = shutil.which("bash")

pytestmark = pytest.mark.skipif(BASH is None, reason="bash not available")


def run(args, cwd, env=None):
    return subprocess.run(
        [BASH, str(UNINSTALL), *args],
        cwd=str(cwd),
        env={**os.environ, **(env or {})},
        capture_output=True,
        text=True,
        timeout=180,
    )


def test_uninstall_removes_agents(tmp_path):
    """Every installed agent file must be gone after uninstall."""
    cfg = tmp_path / "cfg"
    env = {"OPENCODE_CONFIG_DIR": str(cfg)}

    install = subprocess.run(
        [BASH, str(REPO / "install.sh"), "--agent", "opencode"],
        cwd=str(tmp_path), env={**os.environ, **env},
        capture_output=True, text=True, timeout=180,
    )
    assert install.returncode == 0, install.stderr

    installed = sorted(p.name for p in (cfg / "agents").glob("*.md"))
    assert installed, "install produced no agents to remove"

    proc = run(["--agent", "opencode", "--yes"], cwd=tmp_path, env=env)
    assert proc.returncode == 0, proc.stderr

    assert sorted(p.name for p in (cfg / "agents").glob("*.md")) == [], "agents survived the uninstall"
