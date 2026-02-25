from pathlib import Path

from byteops_agent.config import load_agent_config


def test_load_agent_config_reads_defaults():
    root = Path(__file__).resolve().parent.parent
    cfg = load_agent_config(root / "config" / "watchlist.yaml", root / "config" / "policy.yaml")

    assert cfg.watchlist.poll_seconds > 0
    assert len(cfg.watchlist.rss) >= 1
    assert cfg.policy.notifications.desktop.provider == "plyer"
