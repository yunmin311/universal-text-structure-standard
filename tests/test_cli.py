"""Exercise the public CLI: exit status is not a writing-quality verdict."""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DeliveryGateTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(ROOT / 'scripts/validate.py'), *args],
                              cwd=ROOT, capture_output=True, text=True)

    def test_warning_cannot_be_reported_as_quality_pass(self):
        result = self.run_cli('examples/bad/micro-paragraphs.md')
        self.assertEqual(result.returncode, 0)  # Legacy diagnostic mode remains compatible.
        self.assertIn('REVIEW_REQUIRED', result.stdout)
        self.assertIn('SEMANTIC=NOT_EVALUATED', result.stdout)
        strict = self.run_cli('--strict', 'examples/bad/micro-paragraphs.md')
        self.assertEqual(strict.returncode, 1)
        self.assertIn('REVIEW_REQUIRED', strict.stdout)

    def test_clean_document_is_only_static_evidence(self):
        result = self.run_cli('--strict', 'examples/good/compact.md')
        self.assertEqual(result.returncode, 0)
        self.assertIn('STATIC_CLEAN', result.stdout)
        self.assertIn('SEMANTIC=NOT_EVALUATED', result.stdout)

    def test_render_error_blocks_both_modes(self):
        for mode in [[], ['--strict']]:
            result = self.run_cli(*mode, 'examples/bad/fence-unclosed.md')
            self.assertEqual(result.returncode, 1)
            self.assertIn('BLOCKED', result.stdout)

    def test_long_form_delivery_pair(self):
        bad = self.run_cli('--strict', 'examples/bad/block-fragmentation.md')
        self.assertEqual(bad.returncode, 1)
        self.assertIn('PRE-001', bad.stdout)
        good = self.run_cli('--strict', 'examples/good/self-attention.md')
        self.assertEqual(good.returncode, 0)
        self.assertIn('STATIC_CLEAN', good.stdout)

    def test_json_remains_diagnostics_list(self):
        import json
        result = self.run_cli('--strict', '--json', 'examples/bad/micro-paragraphs.md')
        self.assertEqual(result.returncode, 1)
        findings = json.loads(result.stdout)
        self.assertTrue(any(d['rule_id'] == 'PRE-001' for d in findings))

    def test_missing_input_is_not_a_clean_document(self):
        result = self.run_cli('--strict', 'not-a-document.md')
        self.assertEqual(result.returncode, 2)


if __name__ == '__main__':
    unittest.main()
