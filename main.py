import argparse
from datetime import datetime

import pandas
import re
from extract_file import extract_page_in_file, extract_nombre_de_page, extract_liste_de_compte
from extract_table import extract_total, extact_total_montant, extact_total_grand_livre

PATTERN_PIECE = re.compile("[0-9]{6}/[0-9]{2}/[0-9]{2}")

def main():
    # python -m main --file 'Grand_livre de test.pdf'
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--file", action="store", required=True, help="Saisir le nom du fichier du grand livre")
    args = parser.parse_args()
    debut = datetime.today()
    print(f"Début à {debut}")
    liste_compte = extract_liste_de_compte(args.file)

    # Création du dataframe de sortie
    dataFame_sortie = pandas.DataFrame(columns=["Compte", "Intitulé du compte", "Pièce", "Date", "Journal", "Libellé",
                                                "N° facture", "Débit", "Crédit", "Solde Débit", "Solde Crédit"])
    nombre_de_ligne_sortie = 1
    for nb in range(extract_nombre_de_page(args.file)):
        file = extract_page_in_file(args.file, nb)
        for i in range(0, len(file)):
            for j in range(0, len(file[i])):
                if file[i][j] != ['Pièce/F/L', 'Date Cpt', 'Jal', 'L.', 'Libellé', 'N° Facture', 'Débit', 'Crédit',
                                  'Solde Débit', 'Solde Crédit']:
                    if not ligne_null(file[i][j]):
                        # print(f"taille = {len(file[i][j])} et file[{i}][{j}] = {file[i][j]}")
                        if len(file[i][j]) == 10:
                            if extract_total(file[i][j]):
                                montant = extact_total_montant(file[i][j][0])
                                dataFame_sortie.loc[nombre_de_ligne_sortie] = [montant[0], liste_compte[montant[0]],
                                                                               "", "", "", "TOTAL DU COMPTE", "",
                                                                               montant[1], montant[2], montant[3],
                                                                               file[i][j][9]]
                                nombre_de_ligne_sortie = nombre_de_ligne_sortie + 1
                            else:
                                dataFame_sortie.loc[nombre_de_ligne_sortie] = ["", "", file[i][j][0], file[i][j][1],
                                                                               file[i][j][2], file[i][j][4],
                                                                               file[i][j][5], file[i][j][6],
                                                                               file[i][j][7], file[i][j][8],
                                                                               file[i][j][9]]
                                nombre_de_ligne_sortie = nombre_de_ligne_sortie + 1
                        elif len(file[i][j]) == 11:
                            if PATTERN_PIECE.match(file[i][j][0]) is None:
                                dataFame_sortie.loc[nombre_de_ligne_sortie] = ["", "", file[i][j][0], file[i][j][1],
                                                                               file[i][j][2], file[i][j][4],
                                                                               file[i][j][5], file[i][j][7],
                                                                               file[i][j][8], file[i][j][9],
                                                                               file[i][j][10]]
                                nombre_de_ligne_sortie = nombre_de_ligne_sortie + 1
                        elif len(file[i][j]) == 12:
                            if file[i][j][0].startswith('Total Général du Grand-Livre', 0, 28):
                                montant = extact_total_grand_livre(file[i][j][0])
                                dataFame_sortie.loc[nombre_de_ligne_sortie] = ["", "", "", "", "",
                                                                               "Total Général du Grand-Livre", "",
                                                                               montant[0], montant[1], montant[2],
                                                                               file[i][j][-1]]
                                nombre_de_ligne_sortie = nombre_de_ligne_sortie + 1
                            else:
                                if PATTERN_PIECE.match(file[i][j][0]) is not None:
                                    dataFame_sortie.loc[nombre_de_ligne_sortie] = ["", "", file[i][j][0], file[i][j][1],
                                                                                   file[i][j][2], file[i][j][4],
                                                                                   file[i][j][5], file[i][j][-4],
                                                                                   file[i][j][-3], file[i][j][-2],
                                                                                   file[i][j][-1]]
                                    nombre_de_ligne_sortie = nombre_de_ligne_sortie + 1
                                elif extract_total(file[i][j]):
                                    montant = extact_total_montant(file[i][j][0])
                                    dataFame_sortie.loc[nombre_de_ligne_sortie] = [montant[0], liste_compte[montant[0]],
                                                                                   "", "", "", "TOTAL DU COMPTE", "",
                                                                                   montant[1], montant[2], montant[3],
                                                                                   file[i][j][-1]]
                                    nombre_de_ligne_sortie = nombre_de_ligne_sortie + 1
        #print(f"page = {nb}")

    # Ecriture du dataframe de sortie
    dataFame_sortie.to_csv(f"Grand_livre_sans_compte.csv", sep=';', encoding='ANSI', decimal=",", index=False)

    compte = ''
    libelle = ''
    nombre_de_ligne_sortie = nombre_de_ligne_sortie - 1
    while nombre_de_ligne_sortie > 0:
        if dataFame_sortie["Libellé"][nombre_de_ligne_sortie] == "TOTAL DU COMPTE":
            compte = dataFame_sortie["Compte"][nombre_de_ligne_sortie]
            libelle = dataFame_sortie["Intitulé du compte"][nombre_de_ligne_sortie]
        else:
            dataFame_sortie["Compte"][nombre_de_ligne_sortie] = compte
            dataFame_sortie["Intitulé du compte"][nombre_de_ligne_sortie] = libelle

        nombre_de_ligne_sortie = nombre_de_ligne_sortie - 1

    # Ecriture du dataframe de sortie
    dataFame_sortie.to_csv(f"Grand_livre.csv", sep=';', encoding='ANSI', decimal=",", index=False)

    fin = datetime.today()
    print(f"Fin à {fin} pour une durée de {fin - debut}")


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
    if ['', None, 'DEBITEUR', None, None, '0,00', None, '', None, None, None, None] == ligne:
        return True
    return False


if __name__ == '__main__':
    main()
