import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CopyRulesTest(unittest.TestCase):
    def test_prohibited_dash_characters_are_absent(self):
        result = subprocess.run(['git', 'ls-files', '-co', '-X', '.gitignore'], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        failures = []
        binary_suffixes = {'.png', '.jpg', '.jpeg', '.pdf', '.woff', '.woff2'}
        for relative in result.stdout.splitlines():
            path = ROOT / relative
            if not path.is_file() or path.suffix.lower() in binary_suffixes:
                continue
            text = path.read_text(encoding='utf-8', errors='ignore')
            if '\u2013' in text or '\u2014' in text or '-' * 2 in text:
                failures.append(relative)
        self.assertEqual(failures, [])


if __name__ == '__main__':
    unittest.main()
