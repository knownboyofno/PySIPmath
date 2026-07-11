import unittest
from unittest.mock import ANY, mock_open, patch

from numpy import array
from tests.fixtures.fit import fit_fixture
from pandas import DataFrame

import PySIP

class BasicTestSuite(unittest.TestCase):
    """Basic test cases."""

    @patch("builtins.open", mock_open(), create=True)
    @patch('pandas.DataFrame')
    def test_Json_opens_a_file_to_write(self, MockDataFrame):
        PySIP.Json(MockDataFrame(), "foo.json", "bar")
        open.assert_called_with("foo.json", "w")

    @patch("json.dump")
    @patch("builtins.open")
    @patch('pandas.DataFrame')
    def test_Json_dumps_a_dict(self, MockDataFrame, mock_open, mock_dump):
        PySIP.Json(MockDataFrame, "foo.json", "bar")
        self.assertEqual({
            'name': 'foo.json',
            'objectType': 'sipModel',
            'libraryType': 'SIPmath_3_0',
            'dateCreated': ANY,
            'provenance': 'bar',
            'U01': {'rng': []},
            'sips': [],
            'version': '1'
        }, mock_dump.call_args[0][0])


    @patch("metalog.metalog.fit")
    @patch("json.dump")
    @patch("builtins.open")
    def test_Json_respects_setupInputs(self, mock_open, mock_dump, mock_fit):
        self.maxDiff = None
        mock_fit.return_value = fit_fixture()
        fixture = DataFrame(data={
            "Accounts": [10.24313638, 13.69812026, 12.62841292, 2.890162231, 7.60269451],
            "Products": [7.00895936, 11.61220758, 5.07099725, 7.542072262, 13.37670202],
        })
        PySIP.Json(fixture, "foo.json", "bar", setupInputs={
            "bounds": [1,2],
            "boundedness":['u', 'u'],
            "term_saved": [30, 2]
        })
        self.assertDictEqual({
            'arguments': {
                'aCoefficients': [7.125830452134216, 5.024858885140949, 9.189185976260735, -19.642180275195027, -31.30801169522319]},
                'function': 'Metalog_1_0',
                'metadata': {
                    'P25': 7.60269451,
                    'P50': 10.24313638,
                    'P75': 12.62841292,
                    'count': 5.0,
                    'density': ANY,
                    'max': 13.69812026,
                    'mean': 9.4125052602,
                    'min': 2.890162231,
                    'std': 4.336325622060243
                },
                'name': 'Accounts',
                'ref': {'name': 'hdr1', 'source': 'rng'}
        }, mock_dump.call_args[0][0]["sips"][0])

        mock_fit.assert_called_with(
            ANY,
            fit_method='OLS', bounds=[0, 1], boundedness='u',
            term_limit=2, term_lower_bound=2, probs=ANY
        )

    @patch("metalog.metalog.fit")
    @patch("json.dump")
    @patch("builtins.open")
    def test_Json_passes_per_sip_probs_to_the_fit(self, mock_open, mock_dump, mock_fit):
        mock_fit.return_value = fit_fixture()
        fixture = DataFrame(data={
            "Accounts": [10.24313638, 13.69812026, 12.62841292, 2.890162231, 7.60269451],
            "Products": [7.00895936, 11.61220758, 5.07099725, 7.542072262, 13.37670202],
        })
        probs = [
            [0.1, 0.3, 0.5, 0.7, 0.9],
            [0.2, 0.4, 0.6, 0.8, 0.95],
        ]
        PySIP.Json(fixture, "foo.json", "bar", probs=probs)

        mock_fit.assert_any_call(
            ANY, fit_method='OLS', bounds=[0, 1], boundedness='u',
            term_limit=5, term_lower_bound=5, probs=probs[0]
        )
        mock_fit.assert_called_with(
            ANY, fit_method='OLS', bounds=[0, 1], boundedness='u',
            term_limit=5, term_lower_bound=5, probs=probs[1]
        )

    @patch("metalog.metalog.fit")
    @patch("json.dump")
    @patch("builtins.open")
    def test_Json_complains_when_bounds_are_short(self, mock_open, mock_dump, mock_fit):
        mock_fit.return_value = fit_fixture()
        fixture = DataFrame(data={
            "Accounts": [10.24313638, 13.69812026, 12.62841292, 2.890162231, 7.60269451],
            "Products": [7.00895936, 11.61220758, 5.07099725, 7.542072262, 13.37670202],
        })
        with self.assertRaisesRegex(
                ValueError,
                'List length of the input file must be equal to the number of SIPs.'):
            PySIP.Json(fixture, "foo.json", "bar", setupInputs={
                "boundedness": ['u', 'u'],
                "bounds": [],
                "term_saved": [5, 5]
            })

    @patch("metalog.metalog.fit")
    @patch("json.dump")
    @patch("builtins.open")
    def test_Json_complains_when_terms_are_short(self, mock_open, mock_dump, mock_fit):
        mock_fit.return_value = fit_fixture()
        fixture = DataFrame(data={
            "Accounts": [10.24313638, 13.69812026, 12.62841292, 2.890162231, 7.60269451],
            "Products": [7.00895936, 11.61220758, 5.07099725, 7.542072262, 13.37670202],
        })
        with self.assertRaisesRegex(
                ValueError,
                'List length of the input file must be equal to the number of SIPs.'):
            PySIP.Json(fixture, "foo.json", "bar", setupInputs={
                "boundedness": ['u', 'u'],
                "bounds": [[0, 1], [0, 1]],
                "term_saved": [5]
            })

    @patch("metalog.metalog.fit")
    @patch("json.dump")
    @patch("builtins.open")
    def test_Json_complains_about_an_unknown_dependence(self, mock_open, mock_dump, mock_fit):
        mock_fit.return_value = fit_fixture()
        fixture = DataFrame(data={
            "Accounts": [10.24313638, 13.69812026, 12.62841292, 2.890162231, 7.60269451],
            "Products": [7.00895936, 11.61220758, 5.07099725, 7.542072262, 13.37670202],
        })
        with self.assertRaisesRegex(ValueError, "dependence must be"):
            PySIP.Json(fixture, "foo.json", "bar", dependence="dependant")

    @patch("metalog.metalog.fit")
    @patch("json.dump")
    @patch("builtins.open")
    def test_Json_does_not_mutate_setupInputs(self, mock_open, mock_dump, mock_fit):
        mock_fit.return_value = fit_fixture()
        fixture = DataFrame(data={
            "Accounts": [10.24313638, 13.69812026, 12.62841292, 2.890162231, 7.60269451],
            "Products": [7.00895936, 11.61220758, 5.07099725, 7.542072262, 13.37670202],
        })
        setup_inputs = {
            "boundedness": ['u', 'u'],
            "bounds": [[5, 6], [7, 8]],
            "term_saved": [5, 5]
        }
        PySIP.Json(fixture, "foo.json", "bar", setupInputs=setup_inputs)

        self.assertListEqual([[5, 6], [7, 8]], setup_inputs["bounds"])

if __name__ == '__main__':
    unittest.main()
