import unittest
from extract_file import extract_file, extract_page_in_file, extract_nombre_de_page


class TestExtractFile(unittest.TestCase):
    def test_extract_file(self):
        file = extract_file('Grand_livre de test.pdf')
        self.assertTrue(file)

    def test_extract_file_page_1(self):
        file = extract_page_in_file('Grand_livre de test.pdf', 1)
        self.assertTrue(file)

    def test_extract_nombre_de_page(self):
        nombre = extract_nombre_de_page('Grand_livre de test.pdf')
        self.assertEqual(nombre, 2)

if __name__ == '__main__':
    unittest.main()
