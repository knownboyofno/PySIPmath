import json
import tempfile
import unittest
from pathlib import Path

from pandas import DataFrame

import PySIP


class SmokeTestSuite(unittest.TestCase):
    """End-to-end runs against the real metalog, nothing mocked.

    Slower than the rest of the suite, but the only tests that catch
    breakage inside the metalog dependency itself (e.g. the NumPy 2
    np.float_ removal).
    """

    def test_Json_writes_a_library_with_the_real_metalog(self):
        fixture = DataFrame(data={
            "Accounts": [10.2, 13.7, 12.6, 2.9, 7.6, 9.1, 11.3, 8.4,
                         6.2, 10.9, 14.1, 5.8, 9.7, 12.0, 7.1, 10.5,
                         8.9, 11.8, 6.7, 9.4],
            "Products": [7.0, 11.6, 5.1, 7.5, 13.4, 9.8, 6.3, 10.2,
                         8.7, 12.1, 5.9, 9.3, 11.0, 7.8, 10.7, 6.6,
                         12.8, 8.1, 9.9, 7.3],
        })
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "smoke.json"
            PySIP.Json(fixture, str(out), "smoke")
            library = json.loads(out.read_text())

        self.assertEqual('SIPmath_3_0', library['libraryType'])
        self.assertEqual('smoke', library['provenance'])
        self.assertEqual(2, len(library['sips']))
        self.assertEqual(2, len(library['U01']['rng']))
        for sip in library['sips']:
            self.assertEqual('Metalog_1_0', sip['function'])
            self.assertEqual(5, len(sip['arguments']['aCoefficients']))
            self.assertEqual(25, len(sip['metadata']['density']))


if __name__ == '__main__':
    unittest.main()
