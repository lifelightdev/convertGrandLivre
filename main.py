import argparse
import pandas
from extract_file import extract_page_in_file, extract_nombre_de_page, extract_liste_de_compte
from extract_table import extract_total, extact_total_montant


def main():
    # python -m main --file 'Grand_livre de test.pdf'
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--file", action="store", required=True, help="Saisir le nom du fichier du grand livre")
    args = parser.parse_args()
    liste_compte = extract_liste_de_compte(args.file)

    # Création du dataframe de sortie
    dataFame_sortie = pandas.DataFrame(columns=["Compte", "Pièce", "Date", "Journal", "Intitulé du compte", "Libellé",
                                                "N° facture", "Débit", "Crédit", "Solde Débit",
                                                "Solde Crédit"])
    nombre_de_ligne_sortie = 1
    for nb in range(extract_nombre_de_page(args.file)):
        file = extract_page_in_file(args.file, nb)
        for i in range(0, len(file)):
            for j in range(0, len(file[i])):
                if file[i][j] != ['Pièce/F/L', 'Date Cpt', 'Jal', 'L.', 'Libellé', 'N° Facture', 'Débit', 'Crédit',
                                  'Solde Débit', 'Solde Crédit']:
                    if not ligne_null(file[i][j]):
                        if len(file[i][j]) == 10:
                            if extract_total(file[i][j]):
                                montant = extact_total_montant(file[i][j][0])
                                if montant[0] == '005480000101':
                                    print(f"montant = {montant} et file[i][j] = {file[i][j]}")
                                dataFame_sortie.loc[nombre_de_ligne_sortie] = [montant[0], "TOTAL DU COMPTE", "", "",
                                                                               liste_compte[montant[0]], "", "",
                                                                               montant[1], montant[2], montant[3],
                                                                               file[i][j][9]]
                                nombre_de_ligne_sortie = nombre_de_ligne_sortie + 1
                            else:
                                dataFame_sortie.loc[nombre_de_ligne_sortie] = ["", file[i][j][0], file[i][j][1],
                                                                               file[i][j][2], "", file[i][j][4],
                                                                               file[i][j][5], file[i][j][6],
                                                                               file[i][j][7], file[i][j][8],
                                                                               file[i][j][9]]
                                nombre_de_ligne_sortie = nombre_de_ligne_sortie + 1
                        else:
                            if extract_total(file[i][j]):
                                montant = extact_total_montant(file[i][j][0])
                                dataFame_sortie.loc[nombre_de_ligne_sortie] = [montant[0], "TOTAL DU COMPTE", "", "",
                                                                               liste_compte[montant[0]], "", "",
                                                                               montant[1], montant[2], montant[3],
                                                                               file[i][j][-1]]
                                nombre_de_ligne_sortie = nombre_de_ligne_sortie + 1

        print(f"page = {nb}")

    # Ecriture du dataframe de sortie
    dataFame_sortie.to_csv(f"Grand_livre.csv", sep=';', encoding='ANSI', decimal=",", index=False)


def ligne_null(ligne):
    if ['', '', '', '', '', '', '', '', '', ''] == ligne:
        return True
    if ['', '', '', '', '', None, '', None, '', '', '', ''] == ligne:
        return True
    if ['', None, None, None, None, None, None, None, None, ''] == ligne:
        return True
    if ['', None, None, None, None, None, None, None, None, None, None, ''] == ligne:
        return True
    if ['', None, None, None, None, None, None, None, None, None, None, None] == ligne:
        return True
    return False


if __name__ == '__main__':
    main()
