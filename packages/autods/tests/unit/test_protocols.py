from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

import autods.environments.jupyter as jupyter_module
from autods.environments.jupyter import JupyterExecutor
from autods.tools.base import Observation


def test_jupyter_executor_is_importable_from_core() -> None:
    assert JupyterExecutor.__name__ == "JupyterExecutor"


def test_observation_model_defaults() -> None:
    observation = Observation(is_success=True, message="ok")

    assert observation.base64_images is None


def test_jupyter_executor_installs_ipykernel_with_uv_for_uv_venv(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    venv_dir = tmp_path / ".venv"
    bin_dir = venv_dir / "bin"
    bin_dir.mkdir(parents=True)
    python = bin_dir / "python"
    python.touch()
    commands: list[list[str]] = []

    def fake_run(command: list[str], **kwargs: Any) -> Any:
        del kwargs
        commands.append(command)
        return SimpleNamespace(returncode=0, stdout="installed", stderr="")

    monkeypatch.setattr(jupyter_module.subprocess, "run", fake_run)

    executor = JupyterExecutor(tmp_path, env_vars={"VIRTUAL_ENV": str(venv_dir)})
    executor._ensure_ipykernel_installed()

    assert commands == [["uv", "pip", "install", "--python", str(python), "ipykernel"]]
