import unittest
from unittest.mock import ANY, patch

from pandas import DataFrame

from tests.fixtures.fit import fit_fixture

import PySIP


def fixture():
    return DataFrame(data={
        "Accounts": [10.24313638, 13.69812026, 12.62841292, 2.890162231, 7.60269451],
        "Products": [7.00895936, 11.61220758, 5.07099725, 7.542072262, 13.37670202],
    })


class BoundednessTestSuite(unittest.TestCase):
    """Boundedness variant test cases."""

    @patch("metalog.metalog.fit")
    @patch("json.dump")
    @patch("builtins.open")
    def test_Json_unbounded_sips_have_no_bound_arguments(self, mock_open, mock_dump, mock_fit):
        mock_fit.return_value = fit_fixture()
        PySIP.Json(fixture(), "foo.json", "bar", boundedness='u')

        arguments = mock_dump.call_args[0][0]["sips"][0]["arguments"]
        self.assertNotIn('lowerBound', arguments)
        self.assertNotIn('upperBound', arguments)

    @patch("metalog.metalog.fit")
    @patch("json.dump")
    @patch("builtins.open")
    def test_Json_semibounded_lower_sips_have_a_lower_bound(self, mock_open, mock_dump, mock_fit):
        mock_fit.return_value = fit_fixture()
        PySIP.Json(fixture(), "foo.json", "bar", boundedness='sl', bounds=[0])

        arguments = mock_dump.call_args[0][0]["sips"][0]["arguments"]
        self.assertEqual(0, arguments["lowerBound"])
        self.assertNotIn('upperBound', arguments)
        mock_fit.assert_called_with(
            ANY, fit_method='OLS', bounds=[0], boundedness='sl',
            term_limit=5, term_lower_bound=5, probs=ANY
        )

    @patch("metalog.metalog.fit")
    @patch("json.dump")
    @patch("builtins.open")
    def test_Json_semibounded_upper_sips_have_an_upper_bound(self, mock_open, mock_dump, mock_fit):
        mock_fit.return_value = fit_fixture()
        PySIP.Json(fixture(), "foo.json", "bar", boundedness='su', bounds=[100])

        arguments = mock_dump.call_args[0][0]["sips"][0]["arguments"]
        self.assertEqual(100, arguments["upperBound"])
        self.assertNotIn('lowerBound', arguments)

    @patch("metalog.metalog.fit")
    @patch("json.dump")
    @patch("builtins.open")
    def test_Json_bounded_sips_have_both_bounds(self, mock_open, mock_dump, mock_fit):
        mock_fit.return_value = fit_fixture()
        PySIP.Json(fixture(), "foo.json", "bar", boundedness='b', bounds=[0, 100])

        arguments = mock_dump.call_args[0][0]["sips"][0]["arguments"]
        self.assertEqual(0, arguments["lowerBound"])
        self.assertEqual(100, arguments["upperBound"])

    @patch("metalog.metalog.fit")
    @patch("json.dump")
    @patch("builtins.open")
    def test_Json_bounded_sips_have_both_bounds_when_dependent(self, mock_open, mock_dump, mock_fit):
        mock_fit.return_value = fit_fixture()
        PySIP.Json(fixture(), "foo.json", "bar", dependence="dependent",
                   boundedness='b', bounds=[0, 100])

        arguments = mock_dump.call_args[0][0]["sips"][0]["arguments"]
        self.assertEqual(0, arguments["lowerBound"])
        self.assertEqual(100, arguments["upperBound"])

    @patch("metalog.metalog.fit")
    @patch("json.dump")
    @patch("builtins.open")
    def test_Json_raises_for_an_unsupported_boundedness(self, mock_open, mock_dump, mock_fit):
        mock_fit.return_value = fit_fixture()

        with self.assertRaises(ValueError):
            PySIP.Json(fixture(), "foo.json", "bar", boundedness='xx')
        mock_dump.assert_not_called()

    @patch("metalog.metalog.fit")
    @patch("json.dump")
    @patch("builtins.open")
    def test_Json_raises_for_an_unsupported_boundedness_when_dependent(self, mock_open, mock_dump, mock_fit):
        mock_fit.return_value = fit_fixture()

        with self.assertRaises(ValueError):
            PySIP.Json(fixture(), "foo.json", "bar", dependence="dependent",
                       boundedness='xx')
        mock_dump.assert_not_called()


if __name__ == '__main__':
    unittest.main()
