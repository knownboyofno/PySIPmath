import unittest
from unittest.mock import ANY, patch

from PySIP.PySIP3library import HDRrngGenerator


class HDRrngGeneratorTestSuite(unittest.TestCase):
    """HDRrngGenerator test cases."""

    @patch("json.dump")
    @patch("builtins.open")
    def test_default_creates_one_rng_per_sip(self, mock_open, mock_dump):
        rngs = HDRrngGenerator(3)

        self.assertEqual(3, len(rngs))
        for i, rng in enumerate(rngs):
            self.assertDictEqual({
                'name': 'hdr' + str(i + 1),
                'function': 'HDR_2_0',
                'arguments': {
                    'counter': 'PM_Index',
                    'entity': 1,
                    'varId': ANY,
                    'seed3': 0,
                    'seed4': 0
                }
            }, rng)

    @patch("json.dump")
    @patch("builtins.open")
    def test_default_var_ids_increment(self, mock_open, mock_dump):
        rngs = HDRrngGenerator(3)

        var_ids = [rng['arguments']['varId'] for rng in rngs]
        self.assertListEqual(
            [var_ids[0], var_ids[0] + 1, var_ids[0] + 2], var_ids)

    @patch("json.dump")
    @patch("builtins.open")
    def test_int_varid_is_used_as_a_base(self, mock_open, mock_dump):
        rngs = HDRrngGenerator(2, varid=100)

        self.assertEqual(100, rngs[0]['arguments']['varId'])
        self.assertEqual(101, rngs[1]['arguments']['varId'])

    @patch("json.dump")
    @patch("builtins.open")
    def test_all_list_parameters_are_used_elementwise(self, mock_open, mock_dump):
        rngs = HDRrngGenerator(
            2, entity=[5, 6], varid=[100, 200], seed3=[1, 2], seed4=[3, 4])

        self.assertDictEqual({
            'name': 'hdr1',
            'function': 'HDR_2_0',
            'arguments': {
                'counter': 'PM_Index',
                'entity': 5,
                'varId': 100,
                'seed3': 1,
                'seed4': 3
            }
        }, rngs[0])
        self.assertDictEqual({
            'name': 'hdr2',
            'function': 'HDR_2_0',
            'arguments': {
                'counter': 'PM_Index',
                'entity': 6,
                'varId': 200,
                'seed3': 2,
                'seed4': 4
            }
        }, rngs[1])

    @patch("json.dump")
    @patch("builtins.open")
    def test_list_entity_and_varid_with_int_seeds(self, mock_open, mock_dump):
        rngs = HDRrngGenerator(2, entity=[5, 6], varid=[100, 200], seed3=7, seed4=8)

        self.assertDictEqual({
            'name': 'hdr1',
            'function': 'HDR_2_0',
            'arguments': {
                'counter': 'PM_Index',
                'entity': 5,
                'varId': 100,
                'seed3': 7,
                'seed4': 8
            }
        }, rngs[0])
        self.assertEqual(6, rngs[1]['arguments']['entity'])
        self.assertEqual(200, rngs[1]['arguments']['varId'])

    @patch("json.dump")
    @patch("builtins.open")
    def test_list_entity_with_int_varid_increments_var_ids(self, mock_open, mock_dump):
        rngs = HDRrngGenerator(2, entity=[5, 6], varid=100)

        self.assertEqual(100, rngs[0]['arguments']['varId'])
        self.assertEqual(101, rngs[1]['arguments']['varId'])
        self.assertEqual(5, rngs[0]['arguments']['entity'])
        self.assertEqual(6, rngs[1]['arguments']['entity'])

    @patch("json.dump")
    @patch("builtins.open")
    def test_returns_none_when_entity_list_is_too_short(self, mock_open, mock_dump):
        with self.assertLogs("PySIP.PySIP3library", level="ERROR") as logs:
            rngs = HDRrngGenerator(3, entity=[1, 2])

        self.assertIsNone(rngs)
        mock_dump.assert_not_called()
        self.assertIn(
            "Entity needs to be a single integer value or a list at least as long as x.",
            logs.output[0])

    @patch("json.dump")
    @patch("builtins.open")
    def test_returns_none_for_an_unsupported_configuration(self, mock_open, mock_dump):
        with self.assertLogs("PySIP.PySIP3library", level="ERROR") as logs:
            rngs = HDRrngGenerator(2, entity=1, varid=[100, 200])

        self.assertIsNone(rngs)
        mock_dump.assert_not_called()
        self.assertIn(
            "Parameters are not in the correct formats (int, list) or aren't in a supported configuration.",
            logs.output[0])

    @patch("json.dump")
    @patch("builtins.open")
    def test_saves_the_rngs_to_a_seeds_file(self, mock_open, mock_dump):
        rngs = HDRrngGenerator(2)

        open.assert_called_with('HDRseeds.json', 'w')
        self.assertListEqual(rngs, mock_dump.call_args[0][0])


if __name__ == '__main__':
    unittest.main()
