import argparse
import contextlib
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('personal_os', ROOT / 'scripts' / 'personal_os.py')
PERSONAL_OS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PERSONAL_OS)


class PersonalOSTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.vault = self.root / 'vault'
        self.workspace = self.root / 'workspace'
        self.vault.mkdir()
        self.workspace.mkdir()
        self.cfg = {
            'runtime_root': str(self.root),
            'vault': str(self.vault),
            'workspace': str(self.workspace),
            'personal_account': '',
            'personal_calendar': 'primary',
            'work_account': '',
            'work_calendar': '',
        }

    def tearDown(self):
        self.temp.cleanup()

    def meeting_content(self):
        boundary = '-' * 3
        return '\n'.join([
            boundary,
            'type: granola-meeting',
            'date: 2026-08-01',
            'granola_id: meeting-123',
            'status: raw',
            'topics: []',
            boundary,
            '# Product planning',
            '',
            '## Transcript',
            '',
            'Jordan: Launch on August 12. Remm owns the checklist.',
            '',
        ])

    def test_meeting_actions_require_approval(self):
        meetings = self.vault / 'Meetings'
        meetings.mkdir()
        meeting = meetings / 'Product planning - 2026-08-01.md'
        meeting.write_text(self.meeting_content(), encoding='utf-8')
        packet = {
            'summary': 'The team selected an August 12 launch.',
            'proposed_actions': [
                {'task': 'Finish launch checklist', 'assignee': 'Remm', 'due': '2026-08-10'},
                {'task': 'Notify customers', 'assignee': 'Jordan', 'due': '2026-08-11'},
            ],
            'key_decisions': ['Launch on August 12'],
            'topics': ['launch', 'checklist'],
        }
        with mock.patch.object(PERSONAL_OS, 'codex_packet', return_value=packet):
            code = PERSONAL_OS.cmd_granola_process(argparse.Namespace(meeting=''), self.cfg)
        self.assertEqual(code, 0)
        self.assertFalse((self.vault / 'TaskNotes' / 'Tasks').exists())
        reviewed = meeting.read_text(encoding='utf-8')
        self.assertIn('status: review', reviewed)
        self.assertIn('## Proposed Actions', reviewed)

        code = PERSONAL_OS.cmd_granola_approve(
            argparse.Namespace(meeting='meeting-123', actions=['1']),
            self.cfg,
        )
        self.assertEqual(code, 0)
        tasks = list((self.vault / 'TaskNotes' / 'Tasks').glob('*.md'))
        self.assertEqual([path.stem for path in tasks], ['Finish launch checklist'])
        final = meeting.read_text(encoding='utf-8')
        self.assertIn('- [x] Finish launch checklist', final)
        self.assertIn('- [ ] Notify customers', final)
        self.assertIn('status: review', final)
        task = tasks[0].read_text(encoding='utf-8')
        self.assertIn('due: "2026-08-10"', task)

    def test_recurring_task_has_rule_and_next_occurrence(self):
        args = argparse.Namespace(
            title='Prepare weekly update',
            scheduled='2026-08-05T09:00',
            recurrence='DTSTART:20260805T090000;FREQ=WEEKLY;BYDAY=WE',
            owner='Remm',
        )
        code = PERSONAL_OS.cmd_recurring_add(args, self.cfg)
        self.assertEqual(code, 0)
        task = (self.vault / 'TaskNotes' / 'Tasks' / 'Prepare weekly update.md').read_text(encoding='utf-8')
        self.assertIn('scheduled: "2026-08-05T09:00"', task)
        self.assertIn('recurrence: "DTSTART:20260805T090000;FREQ=WEEKLY;BYDAY=WE"', task)

    def test_google_credentials_use_a_temporary_file(self):
        captured = {}

        def fake_run(command, timeout=120, input_text=None):
            del timeout, input_text
            credential_path = Path(command[-1])
            captured['path'] = credential_path
            captured['payload'] = credential_path.read_text(encoding='utf-8')
            return PERSONAL_OS.subprocess.CompletedProcess(command, 0, 'ok', '')

        secrets = {'GOOGLE_CLIENT_ID': 'client-id', 'GOOGLE_CLIENT_SECRET': 'client-secret'}
        with mock.patch.object(PERSONAL_OS, 'doppler_secret', side_effect=lambda name: secrets[name]):
            with mock.patch.object(PERSONAL_OS, 'run', side_effect=fake_run):
                code = PERSONAL_OS.cmd_google_credentials(argparse.Namespace(), self.cfg)
        self.assertEqual(code, 0)
        self.assertIn('client-id', captured['payload'])
        self.assertIn('client-secret', captured['payload'])
        self.assertFalse(captured['path'].exists())

    def test_google_auth_saves_selected_account(self):
        config_path = self.root / 'config.json'
        result = PERSONAL_OS.subprocess.CompletedProcess(['gog'], 0, 'ok', '')
        args = argparse.Namespace(kind='personal', account='remm@example.com', gmail='')
        with mock.patch.object(PERSONAL_OS, 'CONFIG_PATH', config_path):
            with mock.patch.object(PERSONAL_OS, 'run', return_value=result):
                code = PERSONAL_OS.cmd_google_auth(args, self.cfg)
        self.assertEqual(code, 0)
        saved = config_path.read_text(encoding='utf-8')
        self.assertIn('remm@example.com', saved)

    def test_doctor_passes_when_required_dependencies_are_ready(self):
        cfg = dict(self.cfg)
        cfg['personal_account'] = 'remm@example.com'
        plugins = self.vault / '.obsidian' / 'plugins'
        for plugin_id in ('tasknotes', 'dataview', 'google-calendar'):
            manifest = plugins / plugin_id / 'manifest.json'
            manifest.parent.mkdir(parents=True, exist_ok=True)
            manifest.write_text('{}\n', encoding='utf-8')
        granola_auth = self.root / 'granola-auth.json'
        granola_auth.write_text('{}\n', encoding='utf-8')

        def command_result(command):
            if command == ['node', '-v']:
                return True, 'v24.18.1'
            if command == ['codex', 'login', 'status']:
                return True, 'Logged in using ChatGPT'
            return True, 'ready'

        output = io.StringIO()
        with mock.patch.object(PERSONAL_OS, 'GRANOLA_AUTH_PATH', granola_auth):
            with mock.patch.object(PERSONAL_OS.shutil, 'which', return_value='/opt/homebrew/bin/tool'):
                with mock.patch.object(PERSONAL_OS, 'command_detail', side_effect=command_result):
                    with mock.patch.object(PERSONAL_OS.Path, 'exists', return_value=True):
                        with contextlib.redirect_stdout(output):
                            code = PERSONAL_OS.cmd_doctor(argparse.Namespace(), cfg)
        self.assertEqual(code, 0)
        self.assertIn('All required checks pass.', output.getvalue())

    def test_daily_note_is_today_only(self):
        with mock.patch.object(PERSONAL_OS, 'fetch_calendar_events', return_value=[{
            'source': 'Work',
            'title': 'Product sync',
            'start': {'dateTime': '2026-08-01T09:00:00'},
            'end': {'dateTime': '2026-08-01T09:30:00'},
        }]):
            with mock.patch.object(PERSONAL_OS.shutil, 'which', return_value='/opt/homebrew/bin/gog'):
                code = PERSONAL_OS.cmd_daily(argparse.Namespace(date='2026-08-01'), self.cfg)
        self.assertEqual(code, 0)
        note = (self.vault / 'Daily' / '2026-08-01.md').read_text(encoding='utf-8')
        self.assertIn('09:00 | Work | Product sync', note)
        self.assertIn('## Due tasks', note)
        self.assertIn('## Granola review', note)
        self.assertNotIn('Tomorrow', note)


if __name__ == '__main__':
    unittest.main()
