from pathlib import Path

from obs_plugin_manager.catalog import Catalog


def test_seed_and_list(tmp_path: Path) -> None:
    cat = Catalog(state_dir=tmp_path)
    count = cat.seed_builtin()
    assert count >= 1

    plugins = cat.list_plugins()
    assert any(p["plugin_id"] == "obs-websocket" for p in plugins)
