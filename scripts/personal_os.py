#!/usr/bin/env python3
"""OpenClaw Personal OS command surface for a scoped Mac runtime."""

import argparse
import getpass
import hashlib
import hmac
import json
import os
import plistlib
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional


VERSION = '1.0.0'
CONFIG_PATH = Path.home() / '.personal-os' / 'config.json'
GRANOLA_AUTH_PATH = Path.home() / 'Library' / 'Application Support' / 'Granola' / 'supabase.json'
GRANOLA_API = 'https://api.granola.ai'
GRANOLA_FALLBACK_VERSION = '7.452.1'
LONG = '-' * 2


def load_config() -> dict:
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text(encoding='utf-8'))
    runtime = Path(os.environ.get('PERSONAL_OS_ROOT', Path.home() / 'PersonalOS' / 'runtime'))
    return {
        'runtime_root': str(runtime),
        'vault': str(runtime / 'vault'),
        'workspace': str(runtime / 'workspace'),
        'personal_account': '',
        'personal_calendar': 'primary',
        'work_account': '',
        'work_calendar': '',
        'timezone': 'America/New_York',
    }


def save_config(cfg: dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2) + '\n', encoding='utf-8')


def run(command: list[str], timeout: int = 120, input_text: Optional[str] = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        command,
        input=input_text,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def safe_filename(value: str, limit: int = 120) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', value).strip('. ')
    return cleaned[:limit] or 'Untitled'


def parse_frontmatter(content: str) -> tuple[dict, str]:
    boundary = '-' * 3
    if not content.startswith(boundary + '\n'):
        return {}, content
    end = content.find('\n' + boundary + '\n', len(boundary) + 1)
    if end < 0:
        return {}, content
    block = content[len(boundary) + 1:end]
    data = {}
    for line in block.splitlines():
        if ':' not in line or line.startswith(' '):
            continue
        key, value = line.split(':', 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data, content[end + len(boundary) + 2:]


def replace_frontmatter_value(content: str, key: str, value: str) -> str:
    pattern = re.compile(rf'^{re.escape(key)}:\s*.*$', re.MULTILINE)
    if pattern.search(content):
        return pattern.sub(f'{key}: {value}', content, count=1)
    return content


def task_file(
    vault: Path,
    title: str,
    scheduled: str = '',
    due: str = '',
    owner: str = '',
    source: str = '',
    recurrence: str = '',
) -> Path:
    tasks_dir = vault / 'TaskNotes' / 'Tasks'
    tasks_dir.mkdir(parents=True, exist_ok=True)
    path = tasks_dir / f'{safe_filename(title)}.md'
    if path.exists():
        return path
    now = datetime.now().astimezone().isoformat(timespec='milliseconds')
    boundary = '-' * 3
    lines = [
        boundary,
        'type: task',
        'status: open',
        'priority: normal',
        f'title: {json.dumps(title)}',
        f'scheduled: {json.dumps(scheduled)}',
        f'due: {json.dumps(due)}',
        f'owner: {json.dumps(owner)}',
        f'dateCreated: {json.dumps(now)}',
        f'dateModified: {json.dumps(now)}',
        'tags:',
        '  - task',
    ]
    if source:
        lines.append('  - granola')
    if recurrence:
        lines.append(f'recurrence: {json.dumps(recurrence)}')
    lines.extend([boundary, ''])
    if source:
        lines.append(f'Source meeting: [[{source}]]')
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return path


def doctor_check(label: str, passed: bool, detail: str, required: bool = True) -> dict:
    return {'label': label, 'passed': passed, 'detail': detail, 'required': required}


def command_detail(command: list[str]) -> tuple[bool, str]:
    try:
        result = run(command, timeout=30)
    except (OSError, subprocess.TimeoutExpired) as error:
        return False, str(error)
    text = (result.stdout or result.stderr or '').strip().splitlines()
    return result.returncode == 0, text[0] if text else f'exit {result.returncode}'


def cmd_doctor(args, cfg: dict) -> int:
    del args
    vault = Path(cfg['vault']).expanduser()
    checks = []
    required_bins = ['brew', 'node', 'python3', 'codex', 'openclaw', 'qmd', 'gh', 'vercel', 'doppler', 'gog']
    for binary in required_bins:
        path = shutil.which(binary)
        checks.append(doctor_check(binary, bool(path), path or 'missing'))

    if shutil.which('node'):
        passed, detail = command_detail(['node', '-v'])
        major_match = re.search(r'v(\d+)', detail)
        supported = passed and bool(major_match) and int(major_match.group(1)) == 24
        checks.append(doctor_check('Node 24', supported, detail))

    app_paths = {
        'Obsidian app': Path('/Applications/Obsidian.app'),
        'Granola app': Path('/Applications/Granola.app'),
        'Wispr Flow app': Path('/Applications/Wispr Flow.app'),
    }
    for label, path in app_paths.items():
        checks.append(doctor_check(label, path.exists(), str(path)))

    checks.append(doctor_check('Granola sign in', GRANOLA_AUTH_PATH.exists(), str(GRANOLA_AUTH_PATH)))
    checks.append(doctor_check('Obsidian vault', vault.exists(), str(vault)))

    plugin_ids = ['tasknotes', 'dataview', 'google-calendar']
    for plugin_id in plugin_ids:
        manifest = vault / '.obsidian' / 'plugins' / plugin_id / 'manifest.json'
        checks.append(doctor_check(f'Obsidian plugin {plugin_id}', manifest.exists(), str(manifest)))

    if shutil.which('codex'):
        passed, detail = command_detail(['codex', 'login', 'status'])
        checks.append(doctor_check('Codex sign in', passed and 'Logged in' in detail, detail))
    if shutil.which('gh'):
        passed, detail = command_detail(['gh', 'auth', 'status'])
        checks.append(doctor_check('GitHub sign in', passed, detail))
    if shutil.which('vercel'):
        passed, detail = command_detail(['vercel', 'whoami'])
        checks.append(doctor_check('Vercel sign in', passed, detail))
    if shutil.which('doppler'):
        passed, detail = command_detail(['doppler', 'me'])
        checks.append(doctor_check('Doppler sign in', passed, detail))
    if shutil.which('gog'):
        passed, detail = command_detail(['gog', 'auth', 'list'])
        checks.append(doctor_check('Google accounts', passed and bool(detail), detail))
    if shutil.which('qmd'):
        passed, detail = command_detail(['qmd', 'status'])
        checks.append(doctor_check('Vault Recall index', passed, detail))

    launch_domain = f'gui/{os.getuid()}'
    for label in ('com.personal-os.gateway', 'com.personal-os.granola'):
        passed, detail = command_detail(['launchctl', 'print', f'{launch_domain}/{label}'])
        checks.append(doctor_check(f'Background service {label}', passed, detail))

    checks.append(doctor_check('Personal calendar account', bool(cfg.get('personal_account')), cfg.get('personal_account') or 'not configured'))
    checks.append(doctor_check('Work calendar account', bool(cfg.get('work_account')), cfg.get('work_account') or 'optional', required=False))

    required_failures = 0
    print('OpenClaw Personal OS Doctor')
    print()
    for check in checks:
        state = 'PASS' if check['passed'] else ('OPTIONAL' if not check['required'] else 'FIX')
        print(f"[{state}] {check['label']}: {check['detail']}")
        if check['required'] and not check['passed']:
            required_failures += 1
    print()
    if required_failures:
        print(f'{required_failures} required checks need attention.')
        return 1
    print('All required checks pass.')
    return 0


def calendar_sources(cfg: dict) -> list[tuple[str, str, str]]:
    sources = []
    personal_account = cfg.get('personal_account', '')
    if personal_account:
        sources.append(('Personal', personal_account, cfg.get('personal_calendar') or 'primary'))
    work_account = cfg.get('work_account', '')
    if work_account:
        sources.append(('Work', work_account, cfg.get('work_calendar') or 'primary'))
    return sources


def fetch_calendar_events(cfg: dict, target_date: date) -> list[dict]:
    start = f'{target_date.isoformat()}T00:00:00'
    end = f'{(target_date + timedelta(days=1)).isoformat()}T00:00:00'
    events = []
    for source, account, calendar_id in calendar_sources(cfg):
        command = [
            'gog', 'calendar', 'events', calendar_id,
            LONG + 'from', start,
            LONG + 'to', end,
            LONG + 'account', account,
            LONG + 'json',
        ]
        result = run(command, timeout=60)
        if result.returncode != 0:
            continue
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError:
            continue
        rows = payload if isinstance(payload, list) else payload.get('events', payload.get('items', []))
        for row in rows:
            if not isinstance(row, dict):
                continue
            events.append({
                'source': source,
                'title': row.get('summary') or row.get('title') or 'Untitled event',
                'start': row.get('start', {}),
                'end': row.get('end', {}),
            })
    return events


def open_tasks_for_date(vault: Path, target: date) -> list[dict]:
    rows = []
    tasks_dir = vault / 'TaskNotes' / 'Tasks'
    if not tasks_dir.exists():
        return rows
    for path in sorted(tasks_dir.glob('*.md')):
        content = path.read_text(encoding='utf-8', errors='ignore')
        fm, _ = parse_frontmatter(content)
        if fm.get('status', 'open') in {'done', 'completed', 'cancelled'}:
            continue
        scheduled = fm.get('scheduled', '')
        due = fm.get('due', '')
        if scheduled.startswith(target.isoformat()) or due.startswith(target.isoformat()):
            rows.append({'title': fm.get('title') or path.stem, 'path': path})
    return rows


def granola_reviews(vault: Path) -> list[Path]:
    rows = []
    for path in sorted((vault / 'Meetings').glob('*.md')):
        content = path.read_text(encoding='utf-8', errors='ignore')
        fm, _ = parse_frontmatter(content)
        if fm.get('status') == 'review':
            rows.append(path)
    return rows


def event_time(event: dict) -> str:
    start = event.get('start') or {}
    if isinstance(start, str):
        value = start
    else:
        value = start.get('dateTime') or start.get('date') or ''
    match = re.search(r'T(\d{2}:\d{2})', value)
    return match.group(1) if match else 'All day'


def cmd_daily(args, cfg: dict) -> int:
    target = date.fromisoformat(args.date) if args.date else date.today()
    vault = Path(cfg['vault']).expanduser()
    daily_dir = vault / 'Daily'
    daily_dir.mkdir(parents=True, exist_ok=True)
    note_path = daily_dir / f'{target.isoformat()}.md'
    events = fetch_calendar_events(cfg, target) if shutil.which('gog') else []
    tasks = open_tasks_for_date(vault, target)
    reviews = granola_reviews(vault)

    lines = [f'# {target.strftime("%A, %B %d, %Y")}', '', '## Today at a glance', '']
    if events:
        for event in sorted(events, key=event_time):
            lines.append(f"- {event_time(event)} | {event['source']} | {event['title']}")
    else:
        lines.append('- No connected calendar events found.')
    lines.extend(['', '## Due tasks', ''])
    lines.extend(f"- [ ] [[{task['path'].stem}]]" for task in tasks)
    if not tasks:
        lines.append('- No tasks due today.')
    lines.extend(['', '## Granola review', ''])
    lines.extend(f'- [[{meeting.stem}]]' for meeting in reviews)
    if not reviews:
        lines.append('- No meetings waiting for review.')
    lines.extend(['', '## Reminders', '', '- Add reminders here or dictate them through Telegram.', '', '## Notes', '', ''])

    note_path.write_text('\n'.join(lines), encoding='utf-8')
    print(note_path)
    return 0


def cmd_task_add(args, cfg: dict) -> int:
    path = task_file(
        Path(cfg['vault']).expanduser(),
        args.title,
        scheduled=args.scheduled or '',
        owner=args.owner or '',
    )
    print(path)
    return 0


def cmd_recurring_add(args, cfg: dict) -> int:
    path = task_file(
        Path(cfg['vault']).expanduser(),
        args.title,
        scheduled=args.scheduled,
        owner=args.owner or '',
        recurrence=args.recurrence,
    )
    print(path)
    return 0


def cmd_reminder_add(args, cfg: dict) -> int:
    del cfg
    due_clause = ''
    if args.due:
        parsed = datetime.fromisoformat(args.due)
        apple_date = parsed.strftime('%B %d, %Y %I:%M %p')
        due_clause = f', due date:date "{apple_date}"'
    safe_title_value = args.title.replace('"', '\\"')
    script = (
        'tell application "Reminders"\n'
        'set targetList to list "Reminders"\n'
        f'set newReminder to make new reminder in targetList with properties {{name:"{safe_title_value}"{due_clause}}}\n'
        'end tell'
    )
    result = run(['osascript', '-e', script], timeout=30)
    if result.returncode != 0:
        print(result.stderr.strip(), file=sys.stderr)
        return 1
    print(f'Reminder created: {args.title}')
    return 0


def cmd_calendar_add(args, cfg: dict) -> int:
    source_map = {source.lower(): (account, calendar) for source, account, calendar in calendar_sources(cfg)}
    destination = args.source.lower()
    if destination not in source_map:
        print(f'Calendar source is not configured: {args.source}', file=sys.stderr)
        return 1
    account, calendar_id = source_map[destination]
    command = [
        'gog', 'calendar', 'create', calendar_id,
        LONG + 'summary', args.title,
        LONG + 'from', args.start,
        LONG + 'to', args.end,
        LONG + 'account', account,
    ]
    result = run(command, timeout=60)
    if result.returncode != 0:
        print((result.stderr or result.stdout).strip(), file=sys.stderr)
        return 1
    print(result.stdout.strip() or f'Calendar event created: {args.title}')
    return 0


def doppler_secret(name: str) -> str:
    if os.environ.get(name):
        return os.environ[name]
    result = run([
        'doppler', 'secrets', 'get', name,
        LONG + 'plain',
        '-p', 'openclaw-personal-os',
        '-c', 'dev',
    ], timeout=30)
    return result.stdout.strip() if result.returncode == 0 else ''


def cmd_google_credentials(args, cfg: dict) -> int:
    del args, cfg
    client_id = doppler_secret('GOOGLE_CLIENT_ID')
    client_secret = doppler_secret('GOOGLE_CLIENT_SECRET')
    if not client_id or not client_secret:
        print('Add GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET to Doppler first.', file=sys.stderr)
        return 1
    payload = {
        'installed': {
            'client_id': client_id,
            'client_secret': client_secret,
            'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
            'token_uri': 'https://oauth2.googleapis.com/token',
            'redirect_uris': ['http://localhost'],
        }
    }
    with tempfile.TemporaryDirectory(prefix='personal-os-google-') as temp_dir:
        credential_path = Path(temp_dir) / 'client.json'
        credential_path.write_text(json.dumps(payload), encoding='utf-8')
        credential_path.chmod(0o600)
        result = run(['gog', 'auth', 'credentials', str(credential_path)], timeout=60)
    if result.returncode != 0:
        print((result.stderr or result.stdout).strip(), file=sys.stderr)
        return 1
    print('Google OAuth credentials registered from Doppler.')
    return 0


def cmd_google_auth(args, cfg: dict) -> int:
    services = 'calendar,gmail' if args.gmail else 'calendar'
    result = run([
        'gog', 'auth', 'add', args.account,
        LONG + 'services', services,
    ], timeout=300)
    if result.returncode != 0:
        print((result.stderr or result.stdout).strip(), file=sys.stderr)
        return 1
    cfg[f'{args.kind}_account'] = args.account
    cfg[f'{args.kind}_calendar'] = 'primary'
    save_config(cfg)
    print(f'Connected {args.kind} Google account: {args.account}')
    return 0


def granola_tokens() -> Optional[dict]:
    if not GRANOLA_AUTH_PATH.exists():
        return None
    try:
        raw = json.loads(GRANOLA_AUTH_PATH.read_text(encoding='utf-8'))
        return json.loads(raw['workos_tokens'])
    except (OSError, KeyError, json.JSONDecodeError):
        return None


def save_granola_tokens(tokens: dict) -> None:
    raw = json.loads(GRANOLA_AUTH_PATH.read_text(encoding='utf-8'))
    raw['workos_tokens'] = json.dumps(tokens)
    GRANOLA_AUTH_PATH.write_text(json.dumps(raw), encoding='utf-8')


def granola_client_version() -> str:
    plist_path = Path('/Applications/Granola.app/Contents/Info.plist')
    try:
        with plist_path.open('rb') as plist_file:
            data = plistlib.load(plist_file)
        return str(data.get('CFBundleShortVersionString') or GRANOLA_FALLBACK_VERSION)
    except (OSError, plistlib.InvalidFileException):
        return GRANOLA_FALLBACK_VERSION


def granola_request(endpoint: str, body: dict, access_token: str, api_version: int = 1) -> object:
    headers = {
        'X-Client-Version': granola_client_version(),
        'X-Granola-Platform': 'darwin',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',
    }
    request = urllib.request.Request(
        f'{GRANOLA_API}/v{api_version}/{endpoint}',
        data=json.dumps(body).encode(),
        headers=headers,
        method='POST',
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read())


def valid_granola_tokens() -> dict:
    tokens = granola_tokens()
    if not tokens:
        raise RuntimeError('Open Granola and sign in before syncing meetings.')
    expires_at = tokens.get('obtained_at', 0) + tokens.get('expires_in', 0) * 1000
    if expires_at - time.time() * 1000 > 60000:
        return tokens
    headers = {
        'X-Client-Version': granola_client_version(),
        'X-Granola-Platform': 'darwin',
        'Content-Type': 'application/json',
    }
    request = urllib.request.Request(
        f'{GRANOLA_API}/v1/refresh-access-token',
        data=json.dumps({'refresh_token': tokens['refresh_token']}).encode(),
        headers=headers,
        method='POST',
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        refreshed = json.loads(response.read())
    refreshed['obtained_at'] = int(time.time() * 1000)
    for key in ('refresh_token', 'sign_in_method', 'session_id'):
        if key not in refreshed and key in tokens:
            refreshed[key] = tokens[key]
    save_granola_tokens(refreshed)
    return refreshed


def transcript_lines(items: list[dict]) -> list[str]:
    lines = []
    for item in items:
        text = str(item.get('text', '')).strip()
        if not text:
            continue
        speaker = item.get('speaker') or item.get('source') or 'Speaker'
        timestamp = str(item.get('start_timestamp', ''))
        time_match = re.search(r'T(\d{2}:\d{2}:\d{2})', timestamp)
        time_label = time_match.group(1) if time_match else ''
        lines.append(f'{time_label} {speaker}: {text}'.strip())
    return lines


def cmd_granola_sync(args, cfg: dict) -> int:
    del args
    vault = Path(cfg['vault']).expanduser()
    meetings_dir = vault / 'Meetings'
    meetings_dir.mkdir(parents=True, exist_ok=True)
    tokens = valid_granola_tokens()
    access_token = tokens['access_token']
    payload = granola_request('get-documents', {'input': {'limit': 500}}, access_token, api_version=2)
    documents = payload.get('docs', []) if isinstance(payload, dict) else []
    existing_ids = set()
    for path in meetings_dir.glob('*.md'):
        fm, _ = parse_frontmatter(path.read_text(encoding='utf-8', errors='ignore'))
        if fm.get('granola_id'):
            existing_ids.add(fm['granola_id'])

    created = 0
    boundary = '-' * 3
    for document in documents:
        document_id = str(document.get('id', ''))
        if not document_id or document_id in existing_ids:
            continue
        if document.get('status') in {'in_progress', 'recording'}:
            continue
        transcript_payload = granola_request('get-document-transcript', {'document_id': document_id}, access_token)
        items = transcript_payload if isinstance(transcript_payload, list) else transcript_payload.get('transcript', [])
        title = str(document.get('title') or 'Untitled Meeting').strip()
        created_at = str(document.get('created_at') or '')
        date_match = re.match(r'(\d{4}-\d{2}-\d{2})', created_at)
        date_value = date_match.group(1) if date_match else date.today().isoformat()
        path = meetings_dir / f'{safe_filename(title, 70)} - {date_value}.md'
        if path.exists():
            path = meetings_dir / f'{safe_filename(title, 60)} - {date_value}-{document_id[:8]}.md'
        notes = str(document.get('notes_markdown') or document.get('notes_plain') or '').strip()
        content = [
            boundary,
            'type: granola-meeting',
            f'date: {date_value}',
            f'granola_id: {document_id}',
            'status: raw',
            'topics: []',
            boundary,
            f'# {title}',
            '',
            '## Notes',
            '',
            notes,
            '',
            '## Transcript',
            '',
        ]
        content.extend(transcript_lines(items))
        path.write_text('\n'.join(content).rstrip() + '\n', encoding='utf-8')
        created += 1
    print(f'Synced {created} new Granola meetings.')
    return 0


def codex_packet(prompt: str, workspace: Path) -> dict:
    with tempfile.NamedTemporaryFile(prefix='personal-os-codex-', suffix='.json', delete=False) as temp_file:
        output_path = Path(temp_file.name)
    try:
        result = run(
            ['codex', 'exec', '-s', 'read-only', '-C', str(workspace), '-o', str(output_path), '-'],
            timeout=240,
            input_text=prompt,
        )
        if result.returncode != 0:
            raise RuntimeError((result.stderr or result.stdout or 'Codex failed').strip()[:500])
        text = output_path.read_text(encoding='utf-8').strip()
        if text.startswith('```'):
            text = re.sub(r'^```(?:json)?\s*', '', text)
            text = re.sub(r'\s*```$', '', text)
        start = text.find('{')
        end = text.rfind('}')
        if start < 0 or end < start:
            raise RuntimeError('Codex returned no JSON object.')
        return json.loads(text[start:end + 1])
    finally:
        output_path.unlink(missing_ok=True)


def meeting_prompt(transcript: str) -> str:
    return (
        'Goal: turn this meeting transcript into a precise review packet.\n\n'
        'Success means:\n'
        '* Return one JSON object with summary, proposed_actions, key_decisions, and topics.\n'
        '* Write summary as a concise paragraph with the meeting purpose and outcome.\n'
        '* Write proposed_actions as objects with task, assignee, and due fields.\n'
        '* Use an empty string when the transcript gives no assignee or due date.\n'
        '* Include only actions supported by the transcript.\n'
        '* Write key_decisions and topics as arrays of short strings.\n\n'
        'Stop when the JSON object is complete and valid.\n\n'
        'Return this shape:\n'
        '{\n'
        '  "summary": "text",\n'
        '  "proposed_actions": [{"task": "text", "assignee": "text", "due": "text"}],\n'
        '  "key_decisions": ["text"],\n'
        '  "topics": ["text"]\n'
        '}\n\n'
        f'Transcript:\n{transcript[:100000]}'
    )


def insert_after_title(content: str, section: str) -> str:
    match = re.search(r'^# .+$', content, re.MULTILINE)
    if not match:
        return content + '\n' + section
    position = match.end()
    return content[:position] + '\n\n' + section.rstrip() + '\n' + content[position:]


def cmd_granola_process(args, cfg: dict) -> int:
    vault = Path(cfg['vault']).expanduser()
    workspace = Path(cfg['workspace']).expanduser()
    processed = 0
    failed = 0
    for path in sorted((vault / 'Meetings').glob('*.md')):
        content = path.read_text(encoding='utf-8', errors='ignore')
        fm, _ = parse_frontmatter(content)
        if fm.get('status') != 'raw':
            continue
        if args.meeting and args.meeting not in {fm.get('granola_id'), path.name, path.stem}:
            continue
        transcript_match = re.search(r'^## Transcript\s*$\n(.*)', content, re.MULTILINE | re.DOTALL)
        transcript = transcript_match.group(1).strip() if transcript_match else ''
        if not transcript:
            path.write_text(replace_frontmatter_value(content, 'status', 'processed'), encoding='utf-8')
            processed += 1
            continue
        try:
            packet = codex_packet(meeting_prompt(transcript), workspace)
        except (RuntimeError, json.JSONDecodeError) as error:
            print(f'{path.name}: {error}', file=sys.stderr)
            failed += 1
            continue
        summary = str(packet.get('summary', '')).strip()
        actions = packet.get('proposed_actions', []) if isinstance(packet.get('proposed_actions', []), list) else []
        decisions = packet.get('key_decisions', []) if isinstance(packet.get('key_decisions', []), list) else []
        topics = packet.get('topics', []) if isinstance(packet.get('topics', []), list) else []
        section = ['## Summary', '', summary or 'No summary returned.', '', '## Proposed Actions', '']
        for action in actions:
            if not isinstance(action, dict) or not str(action.get('task', '')).strip():
                continue
            details = []
            if str(action.get('assignee', '')).strip():
                details.append(f"owner: {str(action['assignee']).strip()}")
            if str(action.get('due', '')).strip():
                details.append(f"due: {str(action['due']).strip()}")
            suffix = f" ({'; '.join(details)})" if details else ''
            section.append(f"- [ ] {str(action['task']).strip()}{suffix}")
        if len(section) == 6:
            section.append('- No proposed actions.')
        section.extend(['', '## Key Decisions', ''])
        section.extend(f'- {str(value).strip()}' for value in decisions if str(value).strip())
        section.extend([
            '',
            '## Review Instructions',
            '',
            'Review the proposed actions. Ask OpenClaw to approve only the actions that should become real tasks.',
            '',
        ])
        updated = insert_after_title(content, '\n'.join(section))
        updated = replace_frontmatter_value(updated, 'status', 'review')
        topic_values = [str(value).strip() for value in topics if str(value).strip()][:5]
        updated = replace_frontmatter_value(updated, 'topics', '[' + ', '.join(topic_values) + ']')
        path.write_text(updated, encoding='utf-8')
        processed += 1
    print(f'Processed {processed} meetings. {failed} failed.')
    return 1 if failed else 0


def proposed_actions(content: str) -> list[dict]:
    section = re.search(r'^## Proposed Actions\s*$\n(.*?)(?=^## |\Z)', content, re.MULTILINE | re.DOTALL)
    if not section:
        return []
    rows = []
    pattern = re.compile(r'^- \[([ xX])\] (.+)$', re.MULTILINE)
    for index, match in enumerate(pattern.finditer(section.group(1)), 1):
        rows.append({
            'index': index,
            'checked': match.group(1).lower() == 'x',
            'text': match.group(2).strip(),
            'start': section.start(1) + match.start(),
            'end': section.start(1) + match.end(),
            'line': match.group(0),
        })
    return rows


def split_action(value: str) -> tuple[str, str, str]:
    match = re.search(r' \((owner: .*?)?(?:; )?(due: .*)?\)$', value)
    if not match:
        return value, '', ''
    title = value[:match.start()].strip()
    owner = re.sub(r'^owner:\s*', '', match.group(1) or '').strip()
    due = re.sub(r'^due:\s*', '', match.group(2) or '').strip()
    return title, owner, due


def find_meeting(vault: Path, reference: str) -> tuple[Optional[Path], Optional[str]]:
    for path in sorted((vault / 'Meetings').glob('*.md')):
        content = path.read_text(encoding='utf-8', errors='ignore')
        fm, _ = parse_frontmatter(content)
        if reference in {fm.get('granola_id'), path.name, path.stem}:
            return path, content
    return None, None


def cmd_granola_approve(args, cfg: dict) -> int:
    vault = Path(cfg['vault']).expanduser()
    path, content = find_meeting(vault, args.meeting)
    if not path or content is None:
        print(f'Meeting not found: {args.meeting}', file=sys.stderr)
        return 1
    rows = proposed_actions(content)
    if not rows:
        print('No proposed actions found.', file=sys.stderr)
        return 1
    if any(value.lower() == 'all' for value in args.actions):
        selected = {row['index'] for row in rows if not row['checked']}
    else:
        try:
            selected = {int(value) for value in args.actions}
        except ValueError:
            print('Selections must be numbers or all.', file=sys.stderr)
            return 1
    valid = {row['index'] for row in rows}
    if selected - valid:
        print('One or more selected actions do not exist.', file=sys.stderr)
        return 1

    replacements = []
    links = []
    for row in rows:
        if row['index'] not in selected or row['checked']:
            continue
        title, owner, due = split_action(row['text'])
        scheduled = due if re.match(r'^\d{4}-\d{2}-\d{2}', due) else ''
        task_path = task_file(vault, title, due=scheduled, owner=owner, source=path.stem)
        links.append(f'[[{task_path.stem}]]')
        replacements.append((row['start'], row['end'], row['line'].replace('[ ]', '[x]', 1)))
    for start, end, replacement in sorted(replacements, reverse=True):
        content = content[:start] + replacement + content[end:]
    remaining = [row for row in proposed_actions(content) if not row['checked']]
    content = replace_frontmatter_value(content, 'status', 'review' if remaining else 'processed')
    if links:
        content += '\n## Approved Tasks\n\n' + '\n'.join(f'- {link}' for link in links) + '\n'
    path.write_text(content, encoding='utf-8')
    print(f'Created {len(links)} tasks.')
    return 0


def ensure_qmd_collection(vault: Path) -> None:
    result = run(['qmd', 'collection', 'list'], timeout=30)
    if result.returncode == 0 and re.search(r'\bpersonal-os\b', result.stdout):
        return
    result = run(['qmd', 'collection', 'add', str(vault), LONG + 'name', 'personal-os'], timeout=60)
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout).strip())


def cmd_index(args, cfg: dict) -> int:
    vault = Path(cfg['vault']).expanduser()
    ensure_qmd_collection(vault)
    update = run(['qmd', 'update'], timeout=300)
    if update.returncode != 0:
        print((update.stderr or update.stdout).strip(), file=sys.stderr)
        return 1
    if not args.skip_embed:
        embed = run(['qmd', 'embed', '-c', 'personal-os'], timeout=900)
        if embed.returncode != 0:
            print((embed.stderr or embed.stdout).strip(), file=sys.stderr)
            return 1
    print('Vault Recall index updated.')
    return 0


def cmd_recall(args, cfg: dict) -> int:
    vault = Path(cfg['vault']).expanduser()
    ensure_qmd_collection(vault)
    result = run([
        'qmd', 'query', args.query,
        '-c', 'personal-os',
        '-n', str(args.limit),
        LONG + 'format', 'json',
    ], timeout=120)
    if result.returncode != 0:
        print((result.stderr or result.stdout).strip(), file=sys.stderr)
        return 1
    print(result.stdout.strip())
    return 0


def cmd_granola_run(args, cfg: dict) -> int:
    del args
    sync_code = cmd_granola_sync(argparse.Namespace(), cfg)
    process_code = cmd_granola_process(argparse.Namespace(meeting=''), cfg)
    index_code = cmd_index(argparse.Namespace(skip_embed=False), cfg)
    cmd_daily(argparse.Namespace(date=''), cfg)
    return 1 if any((sync_code, process_code, index_code)) else 0


def pin_hash(pin: str) -> str:
    return hashlib.sha256(pin.encode()).hexdigest()


def cmd_set_pin(args, cfg: dict) -> int:
    del args, cfg
    first = getpass.getpass('Choose a PIN: ')
    second = getpass.getpass('Confirm the PIN: ')
    if len(first) < 6 or first != second:
        print('PINs must match and contain at least six characters.', file=sys.stderr)
        return 1
    value = pin_hash(first)
    result = run(['doppler', 'secrets', 'set', f'PERSONAL_OS_PIN_HASH={value}', '-p', 'openclaw-personal-os', '-c', 'dev'])
    if result.returncode != 0:
        print((result.stderr or result.stdout).strip(), file=sys.stderr)
        return 1
    print('PIN hash stored in Doppler.')
    return 0


def cmd_authorize(args, cfg: dict) -> int:
    del cfg
    supplied = args.pin or os.environ.get('PERSONAL_OS_PIN') or getpass.getpass('PIN: ')
    expected = os.environ.get('PERSONAL_OS_PIN_HASH', '')
    if not expected or not hmac.compare_digest(pin_hash(supplied), expected):
        print('PIN authorization failed.', file=sys.stderr)
        return 1
    auth_path = Path.home() / '.personal-os' / 'authorization.json'
    auth_path.parent.mkdir(parents=True, exist_ok=True)
    auth_path.write_text(json.dumps({'expires_at': time.time() + 600}) + '\n', encoding='utf-8')
    auth_path.chmod(0o600)
    print('High risk actions are authorized for ten minutes.')
    return 0


def high_risk_authorized() -> bool:
    auth_path = Path.home() / '.personal-os' / 'authorization.json'
    if not auth_path.exists():
        return False
    try:
        data = json.loads(auth_path.read_text(encoding='utf-8'))
        return float(data.get('expires_at', 0)) > time.time()
    except (OSError, ValueError, json.JSONDecodeError):
        return False


def launch_services(cfg: dict, action: str) -> int:
    domain = f'gui/{os.getuid()}'
    services = [
        ('com.personal-os.gateway', Path.home() / 'Library' / 'LaunchAgents' / 'com.personal-os.gateway.plist'),
        ('com.personal-os.granola', Path.home() / 'Library' / 'LaunchAgents' / 'com.personal-os.granola.plist'),
    ]
    failures = 0
    for label, plist in services:
        target = f'{domain}/{label}'
        if action == 'status':
            result = run(['launchctl', 'print', target], timeout=30)
            state = 'running' if result.returncode == 0 else 'not loaded'
            print(f'{label}: {state}')
            failures += int(result.returncode != 0)
            continue
        if action == 'stop':
            result = run(['launchctl', 'bootout', target], timeout=30)
            if result.returncode not in {0, 3, 113}:
                print((result.stderr or result.stdout).strip(), file=sys.stderr)
                failures += 1
            else:
                print(f'Stopped {label}.')
            continue
        run(['launchctl', 'bootout', target], timeout=30)
        result = run(['launchctl', 'bootstrap', domain, str(plist)], timeout=30)
        if result.returncode != 0:
            print((result.stderr or result.stdout).strip(), file=sys.stderr)
            failures += 1
            continue
        run(['launchctl', 'enable', target], timeout=30)
        print(f'Started {label}.')
    return 1 if failures else 0


def cmd_services_start(args, cfg: dict) -> int:
    del args
    Path(cfg['runtime_root']).expanduser().joinpath('logs').mkdir(parents=True, exist_ok=True)
    cmd_daily(argparse.Namespace(date=''), cfg)
    return launch_services(cfg, 'start')


def cmd_services_status(args, cfg: dict) -> int:
    del args
    return launch_services(cfg, 'status')


def cmd_services_stop(args, cfg: dict) -> int:
    del args
    return launch_services(cfg, 'stop')


def cmd_install_app(args, cfg: dict) -> int:
    del cfg
    allowed = {'obsidian', 'granola', 'wispr-flow'}
    if args.app not in allowed:
        print('This installer supports only the approved app list.', file=sys.stderr)
        return 1
    if not high_risk_authorized():
        print('Authorize with your PIN before installing an app.', file=sys.stderr)
        return 1
    result = run(['brew', 'install', LONG + 'cask', args.app], timeout=900)
    if result.returncode != 0:
        print((result.stderr or result.stdout).strip(), file=sys.stderr)
        return 1
    print(result.stdout.strip())
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='personal-os')
    parser.add_argument('-V', action='version', version=VERSION)
    commands = parser.add_subparsers(dest='command', required=True)

    commands.add_parser('doctor')

    daily = commands.add_parser('daily')
    daily.add_argument('date', nargs='?', default='')

    task = commands.add_parser('task-add')
    task.add_argument('title')
    task.add_argument('scheduled', nargs='?', default='')
    task.add_argument('owner', nargs='?', default='')

    recurring = commands.add_parser('recurring-add')
    recurring.add_argument('title')
    recurring.add_argument('scheduled')
    recurring.add_argument('recurrence')
    recurring.add_argument('owner', nargs='?', default='')

    reminder = commands.add_parser('reminder-add')
    reminder.add_argument('title')
    reminder.add_argument('due', nargs='?', default='')

    calendar = commands.add_parser('calendar-add')
    calendar.add_argument('source', choices=['personal', 'work'])
    calendar.add_argument('title')
    calendar.add_argument('start')
    calendar.add_argument('end')

    commands.add_parser('google-credentials')
    google = commands.add_parser('google-auth')
    google.add_argument('kind', choices=['personal', 'work'])
    google.add_argument('account')
    google.add_argument('gmail', nargs='?', default='', choices=['', 'gmail'])

    commands.add_parser('granola-sync')
    process = commands.add_parser('granola-process')
    process.add_argument('meeting', nargs='?', default='')
    approve = commands.add_parser('granola-approve')
    approve.add_argument('meeting')
    approve.add_argument('actions', nargs='+')
    commands.add_parser('granola-run')

    index = commands.add_parser('index')
    index.add_argument('mode', nargs='?', default='full', choices=['full', 'text'])
    recall = commands.add_parser('recall')
    recall.add_argument('query')
    recall.add_argument('limit', nargs='?', default=8, type=int)

    commands.add_parser('set-pin')
    commands.add_parser('services-start')
    commands.add_parser('services-status')
    commands.add_parser('services-stop')
    authorize = commands.add_parser('authorize')
    authorize.add_argument('pin', nargs='?', default='')
    install = commands.add_parser('install-app')
    install.add_argument('app')
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    cfg = load_config()
    handlers = {
        'doctor': cmd_doctor,
        'daily': cmd_daily,
        'task-add': cmd_task_add,
        'recurring-add': cmd_recurring_add,
        'reminder-add': cmd_reminder_add,
        'calendar-add': cmd_calendar_add,
        'google-credentials': cmd_google_credentials,
        'google-auth': cmd_google_auth,
        'granola-sync': cmd_granola_sync,
        'granola-process': cmd_granola_process,
        'granola-approve': cmd_granola_approve,
        'granola-run': cmd_granola_run,
        'index': cmd_index,
        'recall': cmd_recall,
        'set-pin': cmd_set_pin,
        'services-start': cmd_services_start,
        'services-status': cmd_services_status,
        'services-stop': cmd_services_stop,
        'authorize': cmd_authorize,
        'install-app': cmd_install_app,
    }
    if args.command == 'index':
        args.skip_embed = args.mode == 'text'
    try:
        return handlers[args.command](args, cfg)
    except (RuntimeError, urllib.error.URLError, urllib.error.HTTPError, subprocess.TimeoutExpired) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
