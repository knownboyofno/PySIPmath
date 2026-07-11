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


class DependenceTestSuite(unittest.TestCase):
    """Dependent (copula) mode test cases."""

    @patch("metalog.metalog.fit")
    @patch("json.dump")
    @patch("builtins.open")
    def test_Json_dependent_sips_reference_the_copula(self, mock_open, mock_dump, mock_fit):
        mock_fit.return_value = fit_fixture()
        PySIP.Json(fixture(), "foo.json", "bar", dependence="dependent")

        sips = mock_dump.call_args[0][0]["sips"]
        self.assertDictEqual({
            'source': 'copula',
            'name': 'Gaussian',
            'copulaLayer': 'c1'
        }, sips[0]["ref"])
        self.assertDictEqual({
            'source': 'copula',
            'name': 'Gaussian',
            'copulaLayer': 'c2'
        }, sips[1]["ref"])

    @patch("metalog.metalog.fit")
    @patch("json.dump")
    @patch("builtins.open")
    def test_Json_dependent_contains_a_gaussian_copula(self, mock_open, mock_dump, mock_fit):
        mock_fit.return_value = fit_fixture()
        PySIP.Json(fixture(), "foo.json", "bar", dependence="dependent")

        u01 = mock_dump.call_args[0][0]["U01"]
        self.assertDictEqual({
            'arguments': {
                'correlationMatrix': {
                    'type': 'globalVariables',
                    'value': 'correlationMatrix'
                },
                'rng': ['hdr1', 'hdr2']
            },
            'function': 'GaussianCopula',
            'name': 'Gaussian',
            'copulaLayer': ['c1', 'c2']
        }, u01["copula"][0])

    @patch("metalog.metalog.fit")
    @patch("json.dump")
    @patch("builtins.open")
    def test_Json_dependent_contains_a_global_correlation_matrix(self, mock_open, mock_dump, mock_fit):
        mock_fit.return_value = fit_fixture()
        data = fixture()
        expected_corr = data["Accounts"].corr(data["Products"])
        PySIP.Json(data, "foo.json", "bar", dependence="dependent")

        global_variables = mock_dump.call_args[0][0]["globalVariables"]
        self.assertEqual(1, len(global_variables))
        self.assertEqual('correlationMatrix', global_variables[0]["name"])

        value = global_variables[0]["value"]
        self.assertListEqual(['Accounts', 'Products'], value["columns"])
        self.assertListEqual(['Accounts', 'Products'], value["rows"])

        # Only the non-zero lower triangle of the correlation matrix is kept
        matrix = value["matrix"]
        self.assertEqual(3, len(matrix))
        self.assertDictEqual(
            {'row': 'Accounts', 'col': 'Accounts', 'value': 1.0}, matrix[0])
        self.assertEqual('Products', matrix[1]["row"])
        self.assertEqual('Accounts', matrix[1]["col"])
        self.assertAlmostEqual(expected_corr, matrix[1]["value"])
        self.assertDictEqual(
            {'row': 'Products', 'col': 'Products', 'value': 1.0}, matrix[2])

    @patch("metalog.metalog.fit")
    @patch("json.dump")
    @patch("builtins.open")
    def test_Json_independent_has_no_copula_or_global_variables(self, mock_open, mock_dump, mock_fit):
        mock_fit.return_value = fit_fixture()
        PySIP.Json(fixture(), "foo.json", "bar")

        library = mock_dump.call_args[0][0]
        self.assertNotIn('globalVariables', library)
        self.assertNotIn('copula', library["U01"])

    @patch("metalog.metalog.fit")
    @patch("json.dump")
    @patch("builtins.open")
    def test_Json_uses_a_provided_quantile_correlation_matrix(self, mock_open, mock_dump, mock_fit):
        mock_fit.return_value = fit_fixture()
        probs = [0.1, 0.3, 0.5, 0.7, 0.9]
        quantiles = fixture()
        quantiles.index = probs
        quantile_corr = DataFrame([[1.0, None], [0.5, 1.0]])
        PySIP.Json(quantiles, "foo.json", "bar", dependence="dependent",
                   quantile_corr_matrix=quantile_corr)

        # The SIP index is passed to the fit as quantile probabilities
        mock_fit.assert_called_with(
            ANY, fit_method='OLS', bounds=[0, 1], boundedness='u',
            term_limit=5, term_lower_bound=5, probs=probs
        )

        # The provided matrix is used instead of the data correlations,
        # keeping every non-null entry
        matrix = mock_dump.call_args[0][0]["globalVariables"][0]["value"]["matrix"]
        self.assertListEqual([
            {'row': 'Accounts', 'col': 'Accounts', 'value': 1.0},
            {'row': 'Products', 'col': 'Accounts', 'value': 0.5},
            {'row': 'Products', 'col': 'Products', 'value': 1.0},
        ], matrix)

    @patch("metalog.metalog.fit")
    @patch("json.dump")
    @patch("builtins.open")
    def test_Json_dependent_passes_per_sip_probs_to_the_fit(self, mock_open, mock_dump, mock_fit):
        mock_fit.return_value = fit_fixture()
        probs = [
            [0.1, 0.3, 0.5, 0.7, 0.9],
            [0.2, 0.4, 0.6, 0.8, 0.95],
        ]
        PySIP.Json(fixture(), "foo.json", "bar", dependence="dependent", probs=probs)

        mock_fit.assert_any_call(
            ANY, fit_method='OLS', bounds=[0, 1], boundedness='u',
            term_limit=5, term_lower_bound=5, probs=probs[0]
        )
        mock_fit.assert_called_with(
            ANY, fit_method='OLS', bounds=[0, 1], boundedness='u',
            term_limit=5, term_lower_bound=5, probs=probs[1]
        )


if __name__ == '__main__':
    unittest.main()
