#!/usr/bin/env python3
"""Install system templates without overwriting personal vault content."""

import json
import os
import secrets
import shutil
import stat
import sys
from pathlib import Path


def copy_missing_tree(source: Path, target: Path) -> None:
    for source_path in source.rglob('*'):
        relative = source_path.relative_to(source)
        target_path = target / relative
        if source_path.is_dir():
            target_path.mkdir(parents=True, exist_ok=True)
            continue
        target_path.parent.mkdir(parents=True, exist_ok=True)
        if not target_path.exists():
            shutil.copy2(source_path, target_path)


def copy_system_file(source: Path, target: Path, executable: bool = False) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    if executable:
        target.chmod(target.stat().st_mode | stat.S_IXUSR)


def render_text(source: Path, target: Path, values: dict[str, str]) -> None:
    content = source.read_text(encoding='utf-8')
    for key, value in values.items():
        content = content.replace(key, value)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding='utf-8')


def main() -> int:
    if len(sys.argv) != 3:
        print('Usage: install_runtime.py SYSTEM_ROOT RUNTIME_ROOT')
        return 2

    system_root = Path(sys.argv[1]).expanduser().resolve()
    runtime_root = Path(sys.argv[2]).expanduser().resolve()
    vault_root = runtime_root / 'vault'
    workspace_root = runtime_root / 'workspace'
    bin_root = runtime_root / 'bin'

    runtime_root.mkdir(parents=True, exist_ok=True)
    (runtime_root / 'logs').mkdir(parents=True, exist_ok=True)
    copy_missing_tree(system_root / 'vault-template', vault_root)
    copy_missing_tree(system_root / 'workspace-template', workspace_root)
    copy_system_file(system_root / 'scripts' / 'personal_os.py', bin_root / 'personal_os.py', True)
    copy_system_file(system_root / 'scripts' / 'start_gateway.sh', bin_root / 'start_gateway.sh', True)

    skill_target = workspace_root / 'skills' / 'vault-recall'
    copy_missing_tree(system_root / 'skills' / 'vault-recall', skill_target)
    skill_values = {'__FRONTMATTER_BOUNDARY__': '-' * 3}
    render_text(
        system_root / 'skills' / 'vault-recall' / 'SKILL.template.md',
        skill_target / 'SKILL.md',
        skill_values,
    )

    values = {
        '__HOME__': str(Path.home()),
        '__RUNTIME_ROOT__': str(runtime_root),
    }
    openclaw_target = Path.home() / '.openclaw' / 'openclaw.json'
    if not openclaw_target.exists():
        render_text(system_root / 'config' / 'openclaw.json.template', openclaw_target, values)
        openclaw_target.chmod(stat.S_IRUSR | stat.S_IWUSR)

    approvals_target = Path.home() / '.openclaw' / 'exec-approvals.json'
    if not approvals_target.exists():
        approvals_values = dict(values)
        approvals_values['__EXEC_SOCKET_TOKEN__'] = secrets.token_urlsafe(32)
        render_text(system_root / 'config' / 'exec-approvals.json.template', approvals_target, approvals_values)
        approvals_target.chmod(stat.S_IRUSR | stat.S_IWUSR)

    launch_target = Path.home() / 'Library' / 'LaunchAgents' / 'com.personal-os.granola.plist'
    render_text(system_root / 'config' / 'com.personal-os.granola.plist.template', launch_target, values)
    gateway_launch_target = Path.home() / 'Library' / 'LaunchAgents' / 'com.personal-os.gateway.plist'
    render_text(system_root / 'config' / 'com.personal-os.gateway.plist.template', gateway_launch_target, values)

    config_root = Path.home() / '.personal-os'
    config_root.mkdir(parents=True, exist_ok=True)
    config_path = config_root / 'config.json'
    if not config_path.exists():
        config_path.write_text(json.dumps({
            'system_root': str(system_root),
            'runtime_root': str(runtime_root),
            'vault': str(vault_root),
            'workspace': str(workspace_root),
            'personal_account': '',
            'personal_calendar': 'primary',
            'work_account': '',
            'work_calendar': '',
            'timezone': 'America/New_York',
            'granola_poll_minutes': 60,
        }, indent=2) + '\n', encoding='utf-8')

    print(f'Runtime installed at {runtime_root}')
    print(f'Vault created at {vault_root}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
