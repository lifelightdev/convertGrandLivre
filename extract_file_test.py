import unittest

from extract_file import extract_file


class TestExtractFile(unittest.TestCase):
    def test_extract_file(self):
        file = extract_file('Grand_livre de test.pdf')
        self.assertTrue(file)

if __name__ == '__main__':
    unittest.main()
