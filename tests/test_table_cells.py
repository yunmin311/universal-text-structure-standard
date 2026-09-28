"""Boundary pipes must not consume legitimate empty cells."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('validator', Path(__file__).resolve().parents[1] / 'scripts/validate.py')
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class TableCellTests(unittest.TestCase):
    def test_empty_edge_and_middle_cells(self):
        text = '|步骤|事务 A|事务 B|\n|---|---|---|\n|1|开始||\n|2||开始|\n||结束|结束|\n||||\n'
        self.assertEqual(validator.scan(text), [])

    def test_missing_and_extra_cells_still_fail(self):
        for row in ['|1|开始|', '|1|开始|||']:
            findings = validator.scan('|步骤|事务 A|事务 B|\n|---|---|---|\n' + row)
            self.assertEqual(validator.signature(findings),
                             [{'rule_id': 'REN-007', 'line': 3, 'severity': 'ERROR'}])

    def test_empty_header_and_escaped_pipe(self):
        self.assertEqual(validator.scan('||说明|\n|---|---|\n||`a\\|b`|\n'), [])


if __name__ == '__main__':
    unittest.main()
