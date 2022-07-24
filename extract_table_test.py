import unittest

from extract_table import extract_entete


class TestExtractTable(unittest.TestCase):
    def test_extract_entete(self):
        table = [['Pièce/F/L', 'Date Cpt', 'Jal', 'L.', 'Libellé', 'N° Facture', 'Débit', 'Crédit', 'Solde Débit', 'Solde Crédit'],
                 ['Compte : 103100 Avances de trésorerie', None, None, None, None, None, None, None, None, None],
                 ['000006/03/09', '01/01/2021', 'AN', '', 'A nouveau au \n01/01/2021', '', '', '18 000,00', '', '18 000,00'],
                 ['TOTAL DU COMPTE : 103100', None, None, None, None, None, '0,00', '18 000,00', '0,00', '18 000,00']]

        entete = extract_entete(table, 0)
        self.assertTrue(entete)

if __name__ == '__main__':
    unittest.main()
