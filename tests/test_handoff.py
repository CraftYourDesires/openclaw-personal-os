import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class HandoffTest(unittest.TestCase):
    def test_complete_handoff_package_is_present(self):
        required = [
            ROOT / 'START-HERE.md',
            ROOT / 'guide' / 'index.html',
            ROOT / 'guide' / 'remm-openclaw-personal-os.pdf',
            ROOT / 'output' / 'pdf' / 'remm-personal-os-call-overview.pdf',
            ROOT / 'setup.sh',
            ROOT / 'doctor.sh',
            ROOT / 'status' / 'index.html',
        ]
        self.assertEqual([str(path) for path in required if not path.exists()], [])

    def test_start_file_defines_one_canonical_layout(self):
        start = (ROOT / 'START-HERE.md').read_text(encoding='utf-8')
        self.assertIn('~/Openclaw/system', start)
        self.assertIn('~/Openclaw/runtime', start)
        self.assertIn('https://github.com/CraftYourDesires/openclaw-personal-os', start)
        self.assertIn('Stop when:', start)

    def test_old_runtime_root_is_absent_from_instruction_sources(self):
        sources = [
            ROOT / 'START-HERE.md',
            ROOT / 'README.md',
            ROOT / 'guide' / 'index.html',
            ROOT / 'setup.sh',
            ROOT / 'doctor.sh',
            ROOT / 'scripts' / 'personal_os.py',
            ROOT / 'workspace-template' / 'AGENTS.md',
        ]
        old_root = '~/PersonalOS'
        found = [str(path) for path in sources if old_root in path.read_text(encoding='utf-8')]
        self.assertEqual(found, [])


if __name__ == '__main__':
    unittest.main()
