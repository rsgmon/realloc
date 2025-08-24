import unittest
import tempfile
import os
from pathlib import Path
from realloc.plugins.importers.account.account_csv import CSVAccountImporter


class TestCSVAccountImporter(unittest.TestCase):
    def setUp(self):
        self.account_importer = CSVAccountImporter()
        self.test_csv_content = '''Account Label,Account Id,Symbol,Shares
IRA,E123,AAA,45
IRA,E123,BBB,6.6
IRA,E123,CCC,1520
Taxable,T456,AAA,10
Taxable,T456,DDD,25'''

    def test_name(self):
        self.assertEqual(self.account_importer.name, "csv_account")

    def test_supported_extensions(self):
        self.assertEqual(self.account_importer.supported_extensions, ['.csv'])

    def test_importer(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tf:
            tf.write(self.test_csv_content)
            tf_name = tf.name
            tf.close()

        try:
            accounts = self.account_importer.account_importer(Path(tf_name))

            # Should create two accounts
            self.assertEqual(len(accounts), 2)

            # Check IRA account
            ira = next(acc for acc in accounts if acc.label == "IRA")
            self.assertEqual(ira.account_number, "E123")
            self.assertEqual(ira.cash, 0)
            self.assertEqual(ira.positions["AAA"], 45)
            self.assertEqual(ira.positions["BBB"], 6.6)
            self.assertEqual(ira.positions["CCC"], 1520)

            # Check Taxable account
            taxable = next(acc for acc in accounts if acc.label == "Taxable")
            self.assertEqual(taxable.account_number, "T456")
            self.assertEqual(taxable.cash, 0)
            self.assertEqual(taxable.positions["AAA"], 10)
            self.assertEqual(taxable.positions["DDD"], 25)

        finally:
            os.unlink(tf_name)

    def test_invalid_shares(self):
        invalid_csv = '''Account Label,Account Id,Symbol,Shares
IRA,E123,AAA,invalid'''

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tf:
            tf.write(invalid_csv)
            tf_name = tf.name
            tf.close()

        try:
            with self.assertRaises(ValueError):
                self.account_importer.account_importer(Path(tf_name))
        finally:
            os.unlink(tf_name)


if __name__ == '__main__':
    unittest.main()