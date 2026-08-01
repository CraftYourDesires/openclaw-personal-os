#!/usr/bin/env python3
"""Install the approved Obsidian community plugins from GitHub releases."""

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path


PLUGINS = [
    ('tasknotes', 'callumalpass/tasknotes', True),
    ('dataview', 'blacksmithgu/obsidian-dataview', True),
    ('google-calendar', 'YukiGasai/obsidian-google-calendar', True),
    ('obsidian-excalidraw-plugin', 'zsviczian/obsidian-excalidraw-plugin', False),
]


def fetch_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={'User-Agent': 'openclaw-personal-os'})
    with urllib.request.urlopen(request, timeout=45) as response:
        return json.loads(response.read())


def download(url: str, target: Path) -> None:
    request = urllib.request.Request(url, headers={'User-Agent': 'openclaw-personal-os'})
    with urllib.request.urlopen(request, timeout=90) as response:
        target.write_bytes(response.read())


def install_plugin(vault: Path, plugin_id: str, repository: str) -> str:
    release = fetch_json(f'https://api.github.com/repos/{repository}/releases/latest')
    assets = {asset['name']: asset['browser_download_url'] for asset in release.get('assets', [])}
    plugin_dir = vault / '.obsidian' / 'plugins' / plugin_id
    plugin_dir.mkdir(parents=True, exist_ok=True)
    required = ['main.js', 'manifest.json']
    for filename in required:
        if filename not in assets:
            raise RuntimeError(f'{repository} release is missing {filename}')
        download(assets[filename], plugin_dir / filename)
    if 'styles.css' in assets:
        download(assets['styles.css'], plugin_dir / 'styles.css')
    return str(release.get('tag_name', 'unknown'))


def main() -> int:
    if len(sys.argv) != 2:
        print('Usage: install_obsidian_plugins.py VAULT_PATH')
        return 2
    vault = Path(sys.argv[1]).expanduser().resolve()
    enabled = []
    for plugin_id, repository, should_enable in PLUGINS:
        try:
            version = install_plugin(vault, plugin_id, repository)
            print(f'Installed {plugin_id} {version}')
            if should_enable:
                enabled.append(plugin_id)
        except (urllib.error.URLError, RuntimeError, json.JSONDecodeError) as error:
            print(f'Plugin install failed for {plugin_id}: {error}', file=sys.stderr)
            return 1

    plugin_config = vault / '.obsidian' / 'community-plugins.json'
    plugin_config.write_text(json.dumps(enabled, indent=2) + '\n', encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
