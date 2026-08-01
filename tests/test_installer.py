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
    def test_second_run_preserves_personal_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir) / 'home'
            home.mkdir()
            runtime = home / 'PersonalOS' / 'runtime'
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


if __name__ == '__main__':
    unittest.main()
