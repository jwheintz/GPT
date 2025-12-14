from obs_plugin_manager.paths import detect_obs_paths


def test_detect_obs_paths_does_not_crash() -> None:
    p = detect_obs_paths(obs_root_hint=None)
    assert p is not None
