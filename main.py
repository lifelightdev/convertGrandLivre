import argparse
from datetime import datetime
import pandas
from constante import COLUMNS_NAME, SEPARATEUR_CSV, ENCODING, DECIMAL
from etape_1 import etape_1_liste_compte
from etape_2 import etape_2_create_df
from etape_3 import etape_3_add_count
from etape_4 import etape_4_extract_compte
from etape_5 import etape_5_total
from etape_6 import etape_6_journaux
from extract_file import extract_file

def main():
    debut = datetime.today()
    print(f"Début à {debut}")
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--file", action="store", required=True, help="Saisir le nom du fichier du grand livre")
    parser.add_argument("--copro", action="store", required=True, help="Saisir le nom de la copropriété : Stade ou Nidor")
    parser.add_argument("--etape1", action="store", required=True,
                        help="Etape 1 à True pour ne pas recréer la liste des comptes mais utiliser le fichier csv")
    parser.add_argument("--etape2", action="store", required=True,
                        help="Etape 2 à True pour ne pas recréer le grand livre sans les comptes mais utilisation du fichier CSV")
    parser.add_argument("--etape6", action="store", required=True,
                        help="Etape 6 à True pour générer que les journaux à du grand livre csv")
    args = parser.parse_args()
    file_name = args.file

    if args.copro == 'XXXX':
        liste = extract_file(file_name)
        nombre_de_colonne = 0
        for element in liste:
            if nombre_de_colonne < len(element):
                nombre_de_colonne = len(element)
        print(f"Il y a {nombre_de_colonne} colonnes dans le fichier CSV (soit lignes dans une page du PDF)")
        liste_of_name_colums = []
        for x in range(0, nombre_de_colonne):
            liste_of_name_colums.append(f"{x}")
        df_fichier = pandas.DataFrame(liste, columns = liste_of_name_colums)
        df_fichier.to_csv(f"fichier.csv", sep=SEPARATEUR_CSV, encoding=ENCODING, decimal=DECIMAL, index=False)
        # 1 ligne dans le CSV =  1 page dans le PDF
        # 1 colonne dans le CSV = 1 ligne dans le PDF
        nom_du_syndic = (df_fichier.iloc[0][0])[0]
        if (df_fichier.iloc[0][0])[0].find('GESTIO') > 0:
            # print(f"C'est le syndic {(df_fichier.iloc[0][0])[0]}")
            # print(f"Liste des colonnes du grand livre {df_fichier.iloc[0][5]}")
            # print(f"Colonne Pièce     = {(df_fichier.iloc[0][5])[0]}")  # Pièce = 0
            # print(f"Colonne Date      = {(df_fichier.iloc[0][5])[2]}")  # Date = 2
            # print(f"Colonne Compte    = {(df_fichier.iloc[0][5])[4]}")  # Compte = 4
            # print(f"Colonne Journal   = {(df_fichier.iloc[0][5])[9]}")  # Jal (Journal) = 9
            # print(f"Colonne C-Partie  = {(df_fichier.iloc[0][5])[10]}") # C-Partie = 10
            # print(f"Colonne N° chèque = {(df_fichier.iloc[0][5])[12]}") # N° chèque = 12
            # print(f"Colonne Libellé   = {(df_fichier.iloc[0][5])[14]}") # Libellé = 14
            # print(f"Colonne Débit     = {(df_fichier.iloc[0][5])[18]}") # Débit = 18
            # print(f"Colonne Crédit    = {(df_fichier.iloc[0][5])[20]}") # Crédit = 20
            # print(f"Liste des colonnes du grand livre {df_fichier.iloc[0][6]}")
            # print(f"C'est la copro {(df_fichier.iloc[0][6])[1]}")
            # print(f"Compte {(df_fichier.iloc[0][7])[4]} {(df_fichier.iloc[0][7])[8]}") # Numéro de compte = 4 Et Nom du compte = 8
            # print(f"{(df_fichier.iloc[0][8])[2]} {(df_fichier.iloc[0][8])[4]} {(df_fichier.iloc[0][8])[14]} {(df_fichier.iloc[0][8])[20]}")
            # print(f"{(df_fichier.iloc[0][9])[10]} {(df_fichier.iloc[0][9])[17]} {(df_fichier.iloc[0][9])[18]} {(df_fichier.iloc[0][9])[20]}")
            # print(f"{(df_fichier.iloc[0][10])[10]} {(df_fichier.iloc[0][10])[17]} {(df_fichier.iloc[0][10])[18]} {(df_fichier.iloc[0][10])[20]}")

            df_sortie = pandas.DataFrame(columns=COLUMNS_NAME)
            df_liste_compte = pandas.DataFrame(columns=["Compte", "Intitulé du compte"])
            nb_ligne_sortie = 0
            nombre_de_compte = 0
            intitule_du_compte = ''
            compte = ''

            for page in range(0, len(liste)):
                for index in range(5, len(liste[page])):
                    if ((df_fichier.iloc[page][index])[4]) != None:
                        if ((df_fichier.iloc[page][index])[2]) == None:
                            if compte != (df_fichier.iloc[page][index])[4]:
                                compte = (df_fichier.iloc[page][index])[4]
                                intitule_du_compte = ''
                                if (df_fichier.iloc[page][index])[6] != None:
                                    intitule_du_compte = (df_fichier.iloc[page][index])[6]
                                if (df_fichier.iloc[page][index])[7] != None:
                                        intitule_du_compte = intitule_du_compte + (df_fichier.iloc[page][index])[7]
                                if (df_fichier.iloc[page][index])[8] != None:
                                    intitule_du_compte = intitule_du_compte + (df_fichier.iloc[page][index])[8]
                                df_liste_compte.loc[nombre_de_compte] = [compte, intitule_du_compte]
                                nombre_de_compte = nombre_de_compte + 1
                        else:
                            libelle = (df_fichier.iloc[page][index])[len(df_fichier.iloc[page][index])-8]
                            if libelle == None:
                                libelle = (df_fichier.iloc[page][index])[len(df_fichier.iloc[page][index])-9]
                            debit = (df_fichier.iloc[page][index])[len(df_fichier.iloc[page][index]) - 4]
                            if debit.find(' €') < 0:
                                debit = ''
                            df_sortie.loc[nb_ligne_sortie] = [(df_fichier.iloc[page][index])[4], # Compte
                                                              intitule_du_compte,
                                                              (df_fichier.iloc[page][index])[0],  # Pièce
                                                              (df_fichier.iloc[page][index])[2],  # Date
                                                              (df_fichier.iloc[page][index])[9],  # Journal
                                                              libelle, # Libellé
                                                              " ",                                # N°facture
                                                              debit, # Débit
                                                              (df_fichier.iloc[page][index])[len(df_fichier.iloc[page][index])-2], # Crédit
                                                              " ",                                # "Solde Débit",
                                                              " ",                                # "Solde Crédit",
                                                              " ",                                # "Vérification Débit/Crédit",
                                                              " "                                 # "Vérification Solde"
                                                              ]
                            nb_ligne_sortie = nb_ligne_sortie + 1

            df_sortie.to_csv(f"Grand_livre_{nom_du_syndic}.csv", sep=SEPARATEUR_CSV, encoding=ENCODING, decimal=DECIMAL, index=False)
            df_liste_compte.to_csv(f"Liste_des_comptes_{nom_du_syndic}.csv", sep=SEPARATEUR_CSV, encoding=ENCODING, decimal=DECIMAL, index=False)


    else:
        etape1 = args.etape1
        etape2 = args.etape2
        etape6 = args.etape6

        if etape6 == 'True':
            etape_6_journaux(etape6, "", "", "")
        else:
            liste_compte, max_size_compte = etape_1_liste_compte(etape1, file_name)
            df_sortie1, max_size_libelle = etape_2_create_df(etape2, file_name, liste_compte)
            df_sortie2 = etape_3_add_count(df_sortie1)
            etape_4_extract_compte(df_sortie2)
            df_sortie3 = etape_5_total(df_sortie2, max_size_compte, max_size_libelle)
            etape_6_journaux(etape6, df_sortie3)

    fin = datetime.today()
    print(f"Fin à {fin} pour une durée de {fin - debut}")


if __name__ == '__main__':
    main()
