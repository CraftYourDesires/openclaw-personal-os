import hashlib
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class InstallerTest(unittest.TestCase):
    def test_default_runtime_uses_openclaw_home_folder(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir) / 'home'
            home.mkdir()
            env = dict(os.environ)
            env.pop('PERSONAL_OS_ROOT', None)
            env.update({
                'HOME': str(home),
                'PERSONAL_OS_SKIP_PACKAGES': '1',
                'PERSONAL_OS_SKIP_PLUGINS': '1',
            })
            result = subprocess.run(['bash', str(ROOT / 'setup.sh')], env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            runtime = home / 'Openclaw' / 'runtime'
            self.assertTrue((runtime / 'vault').exists())
            self.assertTrue((runtime / 'workspace').exists())
            self.assertIn(str(runtime), result.stdout)

    def test_second_run_preserves_personal_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir) / 'home'
            home.mkdir()
            runtime = home / 'Openclaw' / 'runtime'
            env = dict(os.environ)
            env.update({
                'HOME': str(home),
                'PERSONAL_OS_ROOT': str(runtime),
                'PERSONAL_OS_SKIP_PACKAGES': '1',
                'PERSONAL_OS_SKIP_PLUGINS': '1',
            })
            first = subprocess.run(['bash', str(ROOT / 'setup.sh')], env=env, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            note = runtime / 'vault' / 'Daily' / '2026-08-01.md'
            note.write_text('private user note\n', encoding='utf-8')
            before = digest(note)

            second = subprocess.run(['bash', str(ROOT / 'setup.sh')], env=env, capture_output=True, text=True)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(before, digest(note))
            self.assertTrue((home / '.openclaw' / 'openclaw.json').exists())
            self.assertTrue((runtime / 'workspace' / 'skills' / 'vault-recall' / 'SKILL.md').exists())
            config = (home / '.personal-os' / 'config.json').read_text(encoding='utf-8')
            self.assertIn('system_root', config)
            self.assertIn(str(runtime), config)
            profile = (home / '.zprofile').read_text(encoding='utf-8') if (home / '.zprofile').exists() else ''
            self.assertIn('.local/bin', profile)


if __name__ == '__main__':
    unittest.main()
