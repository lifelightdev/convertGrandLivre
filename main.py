import argparse
import pandas
from extract_file import extract_file
from extract_table import extract_entete, extract_compte


def main():
    # python -m main --file 'Grand_livre de test.pdf'
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--file", action="store", required=True, help="Saisir le nom du fichier du grand livre")
    args = parser.parse_args()
    file = extract_file(args.file)

    # Création du dataframe de sortie
    dataFame_sortie = pandas.DataFrame(columns=["Compte", "Pièce", "Date", "Journal", "Intitulé du compte", "Libellé",
                                                "N° facture", "Débit", "Crédit", "Solde Débit",
                                                "Solde Crédit"])
    nombre_de_ligne_sortie = 1
    compte = None
    nom_compte = None
    for i in range(1, len(file)):
        if extract_compte(file[i]):
            compte = extract_compte(file[i])[0]
            nom_compte = extract_compte(file[i])[1]
        else:
            print(f"{extract_entete(file,0)}")
            print(f"{file[i]}")
            dataFame_sortie.loc[nombre_de_ligne_sortie] = [compte, file[i][0], file[i][1], file[i][2], nom_compte,
                                                           file[i][4], file[i][5],file[i][6], file[i][7],
                                                           file[i][8], file[i][9]]
            nombre_de_ligne_sortie = nombre_de_ligne_sortie + 1

    # Ecriture du dataframe de sortie
    dataFame_sortie.to_csv(f"Grand_livre.csv", sep=';', encoding='ANSI', decimal=",", index=False)

if __name__ == '__main__':
    main()
