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
from outil import nb_colonne, colums_name, find_debit, find_journal_contre_partie_num_cheque


def main():
    debut = datetime.today()
    print(f"Début à {debut}")
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--file", action="store", required=True, help="Saisir le nom du fichier du grand livre")
    parser.add_argument("--copro", action="store", required=True, help="Saisir le nom de la copropriété : ")
    parser.add_argument("--etape1", action="store",
                        help="Etape 1 à True pour ne pas recréer la liste des comptes mais utiliser le fichier csv")
    parser.add_argument("--etape2", action="store",
                        help="Etape 2 à True pour ne pas recréer le grand livre sans les comptes mais utilisation du fichier CSV")
    parser.add_argument("--etape6", action="store",
                        help="Etape 6 à True pour générer que les journaux à du grand livre csv")
    args = parser.parse_args()
    file_name = args.file

    if args.copro == 'XXXX':
        liste = extract_file(file_name)
        nombre_de_colonne = nb_colonne(liste)
        print(f"Il y a {nombre_de_colonne} colonnes dans le fichier CSV (soit lignes dans une page du PDF)")
        list_of_name_colums = colums_name(nombre_de_colonne)
        df_fichier = pandas.DataFrame(liste, columns = list_of_name_colums)
        # df_fichier.to_csv(f"fichier.csv", sep=SEPARATEUR_CSV, encoding=ENCODING, decimal=DECIMAL, index=False)
        # 1 ligne dans le CSV =  1 page dans le PDF
        # 1 colonne dans le CSV = 1 ligne dans le PDF
        nom_du_syndic = (df_fichier.iloc[0][0])[0]
        df_sortie = pandas.DataFrame(columns=COLUMNS_NAME)
        df_liste_compte = pandas.DataFrame(columns=["Compte", "Intitulé du compte"])
        nb_ligne_sortie = 0
        nombre_de_compte = 0
        intitule_du_compte = ''
        compte = ''

        for page in range(0, len(liste)):
            for index in range(5, len(liste[page])):
                if (df_fichier.iloc[page][index])[4]  != None:
                    date = (df_fichier.iloc[page][index])[2]
                    if date == None or date == 'Date':
                        compte_nouvel_ligne = (df_fichier.iloc[page][index])[4]
                        if compte != compte_nouvel_ligne and compte_nouvel_ligne != 'Compte':
                            compte = compte_nouvel_ligne
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
                        piece = (df_fichier.iloc[page][index])[0]
                        libelle = (df_fichier.iloc[page][index])[len(df_fichier.iloc[page][index])-8]
                        journal, contre_partie, num_cheque = find_journal_contre_partie_num_cheque(df_fichier, index, page)
                        if libelle == None:
                            libelle = (df_fichier.iloc[page][index])[len(df_fichier.iloc[page][index])-9]
                        num_facture = 'Sans objet'
                        debit = (df_fichier.iloc[page][index])[len(df_fichier.iloc[page][index]) - 4]
                        debit = find_debit(debit)
                        credit = (df_fichier.iloc[page][index])[len(df_fichier.iloc[page][index])-2]
                        solde_debit = 0
                        solde_crebit = 0
                        verification_debit_credit = ''
                        verification_solde = 'Sans objet'
                        df_sortie.loc[nb_ligne_sortie] = [compte, intitule_du_compte, piece, date, journal, libelle,
                                                          num_facture, contre_partie, num_cheque, debit, credit,
                                                          solde_debit, solde_crebit, verification_debit_credit,
                                                          verification_solde ]
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
