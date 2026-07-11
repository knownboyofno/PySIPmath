import unittest
from unittest.mock import ANY, patch

from pandas import DataFrame

from tests.fixtures.fit import fit_fixture
from PySIP.PySIP3library import Xlsx


def fixture():
    return DataFrame(data={
        "Accounts": [10.24313638, 13.69812026, 12.62841292, 2.890162231, 7.60269451],
        "Products": [7.00895936, 11.61220758, 5.07099725, 7.542072262, 13.37670202],
    })


class XlsxTestSuite(unittest.TestCase):
    """Xlsx library output test cases."""

    @patch("metalog.metalog.fit")
    @patch("xlsxwriter.Workbook")
    def test_Xlsx_creates_a_workbook_with_a_library_sheet(self, MockWorkbook, mock_fit):
        mock_fit.return_value = fit_fixture()
        Xlsx(fixture(), "foo.xlsx", "bar")

        MockWorkbook.assert_called_once_with("foo.xlsx")
        workbook = MockWorkbook.return_value
        workbook.add_worksheet.assert_called_once_with('Library')
        workbook.close.assert_called_once()

    @patch("metalog.metalog.fit")
    @patch("xlsxwriter.Workbook")
    def test_Xlsx_writes_the_library_properties(self, MockWorkbook, mock_fit):
        mock_fit.return_value = fit_fixture()
        Xlsx(fixture(), "foo.xlsx", "bar")

        worksheet = MockWorkbook.return_value.add_worksheet.return_value
        worksheet.write.assert_any_call('A1', 'PM_Property_Names')
        worksheet.write.assert_any_call('B3', 'bar')
        worksheet.write.assert_any_call('B4', 'Accounts,Products')
        worksheet.write.assert_any_call('B7', 2)  # number of SIPs
        worksheet.write.assert_any_call('B8', 8)  # describe() metadata rows
        worksheet.write.assert_any_call('B11', '3.2b')

    @patch("metalog.metalog.fit")
    @patch("xlsxwriter.Workbook")
    def test_Xlsx_writes_the_sip_columns(self, MockWorkbook, mock_fit):
        mock_fit.return_value = fit_fixture()
        Xlsx(fixture(), "foo.xlsx", "bar")

        worksheet = MockWorkbook.return_value.add_worksheet.return_value
        worksheet.write.assert_any_call(0, 4, 'Variable_1')
        worksheet.write.assert_any_call(1, 4, 'Accounts')
        worksheet.write.assert_any_call(0, 5, 'Variable_2')
        worksheet.write.assert_any_call(1, 5, 'Products')
        worksheet.write.assert_any_call(2, 4, 'F Inverse')
        worksheet.write.assert_any_call(3, 4, 5)    # terms saved
        worksheet.write.assert_any_call(4, 4, 'u')  # boundedness
        worksheet.write.assert_any_call(5, 4, 0)    # lower bound
        worksheet.write.assert_any_call(6, 4, 1)    # upper bound

    @patch("metalog.metalog.fit")
    @patch("xlsxwriter.Workbook")
    def test_Xlsx_writes_provided_seeds_with_incrementing_var_ids(self, MockWorkbook, mock_fit):
        mock_fit.return_value = fit_fixture()
        Xlsx(fixture(), "foo.xlsx", "bar", seeds=[2, 50, 3, 4])

        # With 2 SIPs the seed block starts at row 9 (7 + sip_count)
        worksheet = MockWorkbook.return_value.add_worksheet.return_value
        worksheet.write.assert_any_call(9, 4, 2)    # entity
        worksheet.write.assert_any_call(10, 4, 50)  # var id
        worksheet.write.assert_any_call(11, 4, 3)   # seed3
        worksheet.write.assert_any_call(12, 4, 4)   # seed4
        worksheet.write.assert_any_call(9, 5, 2)
        worksheet.write.assert_any_call(10, 5, 51)  # var id increments per SIP
        worksheet.write.assert_any_call(11, 5, 3)
        worksheet.write.assert_any_call(12, 5, 4)

    @patch("metalog.metalog.fit")
    @patch("xlsxwriter.Workbook")
    def test_Xlsx_writes_default_seeds(self, MockWorkbook, mock_fit):
        mock_fit.return_value = fit_fixture()
        Xlsx(fixture(), "foo.xlsx", "bar")

        worksheet = MockWorkbook.return_value.add_worksheet.return_value
        worksheet.write.assert_any_call(9, 4, 1)   # default entity
        worksheet.write.assert_any_call(11, 4, 0)  # default seed3
        worksheet.write.assert_any_call(12, 4, 0)  # default seed4

    @patch("metalog.metalog.fit")
    @patch("xlsxwriter.Workbook")
    def test_Xlsx_fits_a_metalog_for_each_sip(self, MockWorkbook, mock_fit):
        mock_fit.return_value = fit_fixture()
        Xlsx(fixture(), "foo.xlsx", "bar")

        self.assertEqual(2, mock_fit.call_count)
        mock_fit.assert_called_with(
            ANY, fit_method='OLS', bounds=[0, 1], boundedness='u',
            term_limit=5, term_lower_bound=5
        )

    @patch("metalog.metalog.fit")
    @patch("xlsxwriter.Workbook")
    def test_Xlsx_uses_provided_metadata(self, MockWorkbook, mock_fit):
        mock_fit.return_value = fit_fixture()
        metadata = DataFrame(data={
            "Accounts": {'foo': 1.0},
            "Products": {'foo': 2.0},
        })
        Xlsx(fixture(), "foo.xlsx", "bar", SIPmetadata=metadata)

        # With one metadata row the block sits at row 11 (11 + sip_count - 2)
        worksheet = MockWorkbook.return_value.add_worksheet.return_value
        worksheet.write.assert_any_call('B8', 1)
        worksheet.write.assert_any_call(13, 4, 1.0)
        worksheet.write.assert_any_call(13, 5, 2.0)


if __name__ == '__main__':
    unittest.main()
