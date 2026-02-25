from pathlib import Path

from byteops_agent.app import _path_from_env


def test_path_from_env_uses_default_when_unset(monkeypatch):
    monkeypatch.delenv("BYTEOPS_TEST_PATH", raising=False)
    default = Path("/tmp/default")

    assert _path_from_env("BYTEOPS_TEST_PATH", default) == default


def test_path_from_env_resolves_override(monkeypatch, tmp_path):
    configured = tmp_path / "../config" / "watchlist.yaml"
    monkeypatch.setenv("BYTEOPS_TEST_PATH", str(configured))

    assert _path_from_env("BYTEOPS_TEST_PATH", Path("unused")) == configured.expanduser().resolve()
