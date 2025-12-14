from __future__ import annotations

import json
from pathlib import Path

import click

from obs_plugin_manager.catalog import Catalog
from obs_plugin_manager.ops.download import download_to_cache
from obs_plugin_manager.ops.install import install_or_update, rollback
from obs_plugin_manager.ops.scan import scan_installed
from obs_plugin_manager.paths import detect_obs_paths
from obs_plugin_manager.process import is_obs_running, kill_obs

DEFAULT_STATE_DIR = Path.home() / ".obs_plugin_manager"


def _state_dir(state_dir: str | None) -> Path:
    d = Path(state_dir) if state_dir else DEFAULT_STATE_DIR
    d.mkdir(parents=True, exist_ok=True)
    return d


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option("--state-dir", type=click.Path(path_type=Path), default=None)
@click.option("--obs-root", type=str, default=None, help="Override OBS installation root")
@click.pass_context
def main(ctx: click.Context, state_dir: Path | None, obs_root: str | None) -> None:
    """Manage OBS plugins by scanning folders and installing updates safely."""

    state = _state_dir(str(state_dir) if state_dir else None)
    ctx.ensure_object(dict)
    ctx.obj["state_dir"] = state
    ctx.obj["obs_paths"] = detect_obs_paths(obs_root_hint=obs_root)
    ctx.obj["catalog"] = Catalog(state_dir=state)


@main.command("status")
@click.pass_context
def status_cmd(ctx: click.Context) -> None:
    """Show detected OBS paths and whether OBS is running."""

    obs_paths = ctx.obj["obs_paths"]
    click.echo(json.dumps({
        "obs_running": is_obs_running(),
        "obs_root": str(obs_paths.obs_root) if obs_paths.obs_root else None,
        "user_config_root": str(obs_paths.user_config_root) if obs_paths.user_config_root else None,
    }, indent=2))


@main.group("catalog")
@click.pass_context
def catalog_grp(ctx: click.Context) -> None:
    """Catalog operations."""


@catalog_grp.command("seed")
@click.pass_context
def catalog_seed(ctx: click.Context) -> None:
    """Seed catalog from built-in seed JSON."""

    cat: Catalog = ctx.obj["catalog"]
    count = cat.seed_builtin()
    click.echo(f"Seeded/updated {count} plugin definitions")


@catalog_grp.command("refresh")
@click.pass_context
def catalog_refresh(ctx: click.Context) -> None:
    """Refresh catalog versions from providers (e.g., GitHub releases)."""

    cat: Catalog = ctx.obj["catalog"]
    updated = cat.refresh_versions()
    click.echo(f"Refreshed {updated} plugin(s)")


@catalog_grp.command("import")
@click.argument("source", type=str)
@click.pass_context
def catalog_import(ctx: click.Context, source: str) -> None:
    """Import/merge plugin definitions from a JSON file or URL.

    The JSON must be a list of plugin definition objects (same shape as the seed file).
    """

    cat: Catalog = ctx.obj["catalog"]
    text: str
    if source.lower().startswith(("http://", "https://")):
        import requests

        resp = requests.get(source, timeout=30)
        resp.raise_for_status()
        text = resp.text
    else:
        text = Path(source).read_text(encoding="utf-8")

    data = json.loads(text)
    if not isinstance(data, list):
        raise click.ClickException("Import JSON must be a list")
    count = cat.upsert_plugins(data)
    click.echo(f"Imported/updated {count} plugin definitions")


@main.command("scan")
@click.option("--json", "as_json", is_flag=True, help="Output machine-readable JSON")
@click.pass_context
def scan_cmd(ctx: click.Context, as_json: bool) -> None:
    """Scan OBS plugin folders and report installed plugins."""

    obs_paths = ctx.obj["obs_paths"]
    cat: Catalog = ctx.obj["catalog"]
    installed = scan_installed(obs_paths=obs_paths, catalog=cat)
    if as_json:
        click.echo(json.dumps([x.to_dict() for x in installed], indent=2))
    else:
        for p in installed:
            installed_v = p.installed_version or "unknown"
            click.echo(f"{p.plugin_id}\t{p.name}\t{installed_v}\t({p.location})")


@main.command("updates")
@click.option("--json", "as_json", is_flag=True)
@click.pass_context
def updates_cmd(ctx: click.Context, as_json: bool) -> None:
    """Show plugins with updates available."""

    obs_paths = ctx.obj["obs_paths"]
    cat: Catalog = ctx.obj["catalog"]
    installed = scan_installed(obs_paths=obs_paths, catalog=cat)
    updates = cat.compute_updates(installed)

    if as_json:
        click.echo(json.dumps([u.to_dict() for u in updates], indent=2))
        return

    if not updates:
        click.echo("No updates detected")
        return

    for u in updates:
        installed_v = u.installed_version or "unknown"
        click.echo(
            f"{u.plugin_id}\t{u.name}\tinstalled={installed_v}\tlatest={u.latest_version}"
        )


@main.command("recommend")
@click.pass_context
def recommend_cmd(ctx: click.Context) -> None:
    """List suggested plugins not currently installed."""

    obs_paths = ctx.obj["obs_paths"]
    cat: Catalog = ctx.obj["catalog"]
    installed = scan_installed(obs_paths=obs_paths, catalog=cat)
    recs = cat.recommend(installed)
    if not recs:
        click.echo("No recommendations (or catalog empty). Try: obs-plugin-manager catalog seed")
        return
    for p in recs:
        click.echo(f"{p['plugin_id']}\t{p['name']}\t{p.get('description','')}")


@main.command("obs")
@click.argument("action", type=click.Choice(["is-running", "kill"], case_sensitive=False))
def obs_cmd(action: str) -> None:
    """OBS process controls (query / kill)."""

    if action.lower() == "is-running":
        click.echo("running" if is_obs_running() else "stopped")
        return

    if action.lower() == "kill":
        kill_obs(force=True)
        click.echo("kill-sent")
        return


@main.command("download")
@click.argument("plugin_id", type=str)
@click.pass_context
def download_cmd(ctx: click.Context, plugin_id: str) -> None:
    """Download a plugin package to cache (no install)."""

    cat: Catalog = ctx.obj["catalog"]
    state_dir: Path = ctx.obj["state_dir"]

    meta = cat.get_plugin(plugin_id)
    if not meta:
        raise click.ClickException(f"Unknown plugin_id '{plugin_id}'. Seed catalog first.")
    url = meta.get("download_url")
    if not url:
        raise click.ClickException(
            f"No download_url in catalog for '{plugin_id}'. Run: obs-plugin-manager catalog refresh"
        )

    path = download_to_cache(url=str(url), state_dir=state_dir, filename_prefix=plugin_id)
    click.echo(json.dumps({"plugin_id": plugin_id, "downloaded": str(path)}, indent=2))


@main.command("install")
@click.argument("plugin_id", type=str)
@click.option("--allow-kill-obs", is_flag=True, help="Kill OBS if running")
@click.pass_context
def install_cmd(ctx: click.Context, plugin_id: str, allow_kill_obs: bool) -> None:
    """Download and install/update a plugin (archives last 2 versions)."""

    cat: Catalog = ctx.obj["catalog"]
    obs_paths = ctx.obj["obs_paths"]
    state_dir: Path = ctx.obj["state_dir"]

    result = install_or_update(
        plugin_id=plugin_id,
        catalog=cat,
        obs_paths=obs_paths,
        state_dir=state_dir,
        allow_kill_obs=allow_kill_obs,
    )
    click.echo(json.dumps(result, indent=2))


@main.command("rollback")
@click.argument("plugin_id", type=str)
@click.option("--index", type=int, default=1, help="1=most recent backup, 2=second most recent")
@click.option("--allow-kill-obs", is_flag=True, help="Kill OBS if running")
@click.pass_context
def rollback_cmd(ctx: click.Context, plugin_id: str, index: int, allow_kill_obs: bool) -> None:
    """Rollback a plugin using archived backups."""

    obs_paths = ctx.obj["obs_paths"]
    state_dir: Path = ctx.obj["state_dir"]

    result = rollback(
        plugin_id=plugin_id,
        obs_paths=obs_paths,
        state_dir=state_dir,
        backup_index=index,
        allow_kill_obs=allow_kill_obs,
    )
    click.echo(json.dumps(result, indent=2))
