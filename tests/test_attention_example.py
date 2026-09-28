"""Run the published teaching code and compare hand-computed results."""
import contextlib
import io
from pathlib import Path
import re
import unittest

EXAMPLE = Path(__file__).resolve().parents[1] / 'examples/good/self-attention.md'


class AttentionExampleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        code, = re.findall(r'```python\n(.*?)\n```', EXAMPLE.read_text(), re.S)
        cls.namespace = {}
        cls.printed = io.StringIO()
        with contextlib.redirect_stdout(cls.printed):
            exec(compile(code, str(EXAMPLE), 'exec'), cls.namespace)

    def test_published_outputs(self):
        self.assertEqual(self.printed.getvalue(),
                         'full [[0.669762, 0.330238], [0.330238, 0.669762]]\n'
                         'causal [[1.0, 0.0], [0.330238, 0.669762]]\n')

    def test_values_are_aggregated_not_replaced_by_weights(self):
        # Equal scores yield equal weights; non-identity V distinguishes AV from A.
        weights, output = self.namespace['attention'](
            [[0.0, 0.0]], [[1.0, 0.0], [0.0, 1.0]],
            [[2.0, 4.0, 6.0], [4.0, 8.0, 10.0]], [[True, True]])
        self.assertEqual(weights, [[0.5, 0.5]])
        self.assertEqual(output, [[3.0, 6.0, 8.0]])

    def test_empty_allowed_set_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'allowed key'):
            self.namespace['attention']([[1.0]], [[1.0]], [[2.0]], [[False]])

    def test_large_finite_scores_do_not_overflow(self):
        weights, output = self.namespace['attention'](
            [[1000.0]], [[1000.0], [999.0]], [[3.0], [8.0]], [[True, True]])
        self.assertEqual(weights, [[1.0, 0.0]])
        self.assertEqual(output, [[3.0]])


if __name__ == '__main__':
    unittest.main()
