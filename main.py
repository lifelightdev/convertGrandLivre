import argparse
from datetime import datetime

import pandas
import re
from extract_file import extract_page_in_file, extract_nombre_de_page, extract_liste_de_compte
from extract_table import extract_total, extact_total_montant, extact_total_grand_livre

PATTERN_PIECE = re.compile("[0-9]{6}/[0-9]{2}/[0-9]{2}")

def main():
    # python -m main --file 'Grand_livre de test.pdf --etape '1'
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--file", action="store", required=True, help="Saisir le nom du fichier du grand livre")
    parser.add_argument("--etape", action="store", required=False, help="Saisir le nom du fichier du grand livre")
    args = parser.parse_args()
    file_name = args.file
    etape = args.etape
    liste_compte = []
    if etape == '1':
        df_liste_compte = pandas.read_csv('Etape_1_liste_des_comptes.csv')
        for index in df_liste_compte.index:
            liste_compte[df_liste_compte.iloc[0, index]] = df_liste_compte.iloc[1, index]
    else:
        debut, fin_etape_1, liste_compte = etape_1_find_count_list(file_name)

    df_sortie, fin_etape_2, nombre_de_ligne_sortie = etape_2_create_df(file_name, fin_etape_1, liste_compte)

    compte, fin_etape_3 = etape_3_add_count(df_sortie, fin_etape_2, nombre_de_ligne_sortie)

    etape_4_total(compte, df_sortie, fin_etape_3)

    liste_journaux = df_sortie.Journal.unique()
    df_journaux = df_sortie.sort_values('Journal')
    print(f"df_journaux = {df_journaux}")
    df_journaux.to_csv("journaux.csv")

    fin = datetime.today()
    print(f"Fin à {fin} pour une durée de {fin - debut}")


def etape_1_find_count_list(file):
    debut = datetime.today()
    print(f"Début de l'étape 1 (recherche des comptes et leurs libellé) à {debut}")
    liste_compte = extract_liste_de_compte(file)
    fin_etape_1 = datetime.today()
    print(f"Fin de l'étape 1 {fin_etape_1} d'une durée de {fin_etape_1 - debut}")
    return debut, fin_etape_1, liste_compte


def etape_2_create_df(file_name, fin_etape_1, liste_compte):
    # Création du dataframe de sortie
    df_sortie = pandas.DataFrame(columns=["Compte", "Intitulé du compte", "Pièce", "Date", "Journal", "Libellé",
                                          "N° facture", "Débit", "Crédit", "Solde Débit", "Solde Crédit",
                                          "Message Débit/Crédit", "Message Solde Débit", "Message Solde Crédit"])
    nb_ligne_sortie = 1
    solde_debit = 0
    solde_crebit = 0
    solde_total_debit = 0
    solde_total_credit = 0
    for nb in range(extract_nombre_de_page(file_name)):
        file = extract_page_in_file(file_name, nb)
        for i in range(0, len(file)):
            for j in range(0, len(file[i])):
                if file[i][j] != ['Pièce/F/L', 'Date Cpt', 'Jal', 'L.', 'Libellé', 'N° Facture', 'Débit', 'Crédit',
                                  'Solde Débit', 'Solde Crédit']:
                    if not ligne_null(file[i][j]):
                        # print(f"taille = {len(file[i][j])} et file[{i}][{j}] = {file[i][j]} et nb = {nb}")
                        if len(file[i][j]) == 10:
                            if extract_total(file[i][j]):
                                nb_ligne_sortie, solde_crebit, solde_debit = ajout_ligne_total(df_sortie, file, i,
                                                                                               j,
                                                                                               liste_compte,
                                                                                               nb_ligne_sortie, 9)
                            else:
                                df_sortie.loc[nb_ligne_sortie] = ["", "", file[i][j][0], file[i][j][1],
                                                                         file[i][j][2], file[i][j][4], file[i][j][5],
                                                                         zero_if_empty(file[i][j][6]),
                                                                         zero_if_empty(file[i][j][7]),
                                                                         zero_if_empty(file[i][j][8]),
                                                                         zero_if_empty(file[i][j][9]), "", "", ""]
                                nb_ligne_sortie = nb_ligne_sortie + 1
                        elif len(file[i][j]) == 11:
                            if PATTERN_PIECE.match(file[i][j][0]) is None:
                                df_sortie.loc[nb_ligne_sortie] = ["", "", file[i][j][0], file[i][j][1],
                                                                         file[i][j][2], file[i][j][4], file[i][j][5],
                                                                         zero_if_empty(file[i][j][7]),
                                                                         zero_if_empty(file[i][j][8]),
                                                                         zero_if_empty(file[i][j][9]),
                                                                         zero_if_empty(file[i][j][10]), ""]
                                nb_ligne_sortie = nb_ligne_sortie + 1
                        elif len(file[i][j]) == 12:
                            if file[i][j][0].startswith('Total Général du Grand-Livre', 0, 28):
                                montant = extact_total_grand_livre(file[i][j][0])
                                df_sortie.loc[nb_ligne_sortie] = ["", "", "", "", "",
                                                                         "Total Général du Grand-Livre", "",
                                                                         zero_if_empty(montant[0]),
                                                                         zero_if_empty(montant[1]),
                                                                         zero_if_empty(montant[2]),
                                                                         zero_if_empty(file[i][j][-1]), "", "", ""]
                                nb_ligne_sortie = nb_ligne_sortie + 1
                            else:
                                if PATTERN_PIECE.match(file[i][j][0]) is not None:
                                    df_sortie.loc[nb_ligne_sortie] = ["", "", file[i][j][0], file[i][j][1],
                                                                             file[i][j][2], file[i][j][4],
                                                                             file[i][j][5],
                                                                             zero_if_empty(file[i][j][-4]),
                                                                             zero_if_empty(file[i][j][-3]),
                                                                             zero_if_empty(file[i][j][-2]),
                                                                             zero_if_empty(file[i][j][-1]), "", "", ""]
                                    nb_ligne_sortie = nb_ligne_sortie + 1
                                elif extract_total(file[i][j]):
                                    nb_ligne_sortie, solde_crebit, solde_debit = ajout_ligne_total(df_sortie, file, i,
                                                                                                   j,
                                                                                                   liste_compte,
                                                                                                   nb_ligne_sortie, -1)
                        if len(file[i][j]) == 2:
                            if extract_total(file[i][j]):
                                nb_ligne_sortie, solde_crebit, solde_debit = ajout_ligne_total(df_sortie, file, i, j,
                                                                                               liste_compte,
                                                                                               nb_ligne_sortie, 1)
                        solde_ligne = convert_montant(df_sortie['Crédit'][nb_ligne_sortie - 1]) - convert_montant(df_sortie['Débit'][nb_ligne_sortie - 1])
                        if df_sortie["Libellé"][nb_ligne_sortie - 1] != "TOTAL DU COMPTE":
                            if solde_ligne > 0:
                                if solde_debit > 0:
                                    solde_crebit = solde_crebit + solde_ligne
                                    solde_debit = 0
                                else:
                                    solde_crebit = solde_crebit + solde_ligne - solde_debit
                                    solde_debit = 0
                            else:
                                if solde_crebit > 0:
                                    solde_debit = solde_debit + solde_ligne - solde_crebit
                                    solde_crebit = 0
                                else:
                                    solde_crebit = solde_crebit - solde_ligne
                                    solde_debit = 0
                        df_sortie['Message Solde Débit'][nb_ligne_sortie - 1] = - solde_debit
                        df_sortie['Message Solde Crédit'][nb_ligne_sortie - 1] = solde_crebit


        # print(f"page = {nb}")
    fin_etape_2 = datetime.today()
    print(f"Fin de l'étape 2 (la création du fichier) à {fin_etape_2} pour une durée de {fin_etape_2 - fin_etape_1}")
    # Ecriture du dataframe de sortie
    df_sortie.to_csv(f"Etape_2_Grand_livre_sans_compte.csv", sep=';', encoding='ANSI', decimal=",", index=False)
    return df_sortie, fin_etape_2, nb_ligne_sortie


def ajout_ligne_total(df_sortie, file, i, j, liste_compte, nombre_de_ligne_sortie, id_solde_crebit):
    montant = extact_total_montant(file[i][j][0])
    df_sortie.loc[nombre_de_ligne_sortie] = [montant[0], liste_compte[montant[0]], "", "", "", "TOTAL DU COMPTE", "",
                                             zero_if_empty(montant[1]), zero_if_empty(montant[2]),
                                             zero_if_empty(montant[3]), zero_if_empty(file[i][j][id_solde_crebit]), "",
                                             "", ""]
    nombre_de_ligne_sortie = nombre_de_ligne_sortie + 1
    return nombre_de_ligne_sortie, 0, 0


def etape_3_add_count(dataFame_sortie, fin_etape_2, nombre_de_ligne_sortie):
    compte = ''
    libelle = ''
    nombre_de_ligne_sortie = nombre_de_ligne_sortie - 1
    while nombre_de_ligne_sortie > 0:
        if dataFame_sortie["Libellé"][nombre_de_ligne_sortie] == "TOTAL DU COMPTE":
            compte = dataFame_sortie["Compte"][nombre_de_ligne_sortie]
            libelle = dataFame_sortie["Intitulé du compte"][nombre_de_ligne_sortie]
            if libelle.startswith(' Copropriétaire ', 0, 17):
                dataFame_sortie["Compte"][nombre_de_ligne_sortie] = '450' + dataFame_sortie["Compte"][nombre_de_ligne_sortie]
        else:
            if libelle.startswith(' Copropriétaire ', 0, 17):
                if not compte.startswith('450', 0, 3):
                    compte = '450' + compte
            dataFame_sortie["Compte"][nombre_de_ligne_sortie] = compte
            dataFame_sortie["Intitulé du compte"][nombre_de_ligne_sortie] = libelle
        nombre_de_ligne_sortie = nombre_de_ligne_sortie - 1
    fin_etape_3 = datetime.today()
    print(f"Fin de l'étape 3 (écriture des comptes) à {fin_etape_3} pour une durée de {fin_etape_3 - fin_etape_2}")
    # Ecriture du dataframe de sortie
    dataFame_sortie.to_csv(f"Etape_3_Grand_livre_avec_compte.csv", sep=';', encoding='ANSI', decimal=",", index=False)
    return compte, fin_etape_3


def etape_4_total(compte, dataFame_sortie, fin_etape_3):
    total_debit = 0
    total_credit = 0
    total_complet_debit = 0
    total_complet_credit = 0
    message = ''
    for index in dataFame_sortie.index:
        if compte == dataFame_sortie["Compte"][index]:
            if dataFame_sortie["Libellé"][index] == "TOTAL DU COMPTE":
                total_debit = round(float(total_debit), 2)
                total_credit = round(float(total_credit), 2)
                if float(total_debit) != convert_montant(dataFame_sortie["Débit"][index]):
                    message = f"{message}Le total des débits ({float(total_debit)}) " \
                              f"n'est pas égale au total du grand livre " \
                              f"({convert_montant(dataFame_sortie['Débit'][index])}) \n"
                if float(total_credit) != convert_montant(dataFame_sortie["Crédit"][index]):
                    message = f"{message}Le total des crédits ({total_credit}) " \
                              f"n'est pas égale au total du grand livre ({dataFame_sortie['Crédit'][index]}) \n"
                if len(message) > 0:
                    dataFame_sortie['Message Débit/Crédit'][index] = message
                else:
                    dataFame_sortie['Message Débit/Crédit'][index] = 'OK'
                total_complet_debit = total_complet_debit + total_debit
                total_complet_credit = total_complet_credit + total_credit
                total_debit = 0
                total_credit = 0
                message = ''
                compte = dataFame_sortie["Compte"][index + 1]
            elif dataFame_sortie["Libellé"][index] == 'Total Général du Grand-Livre':
                total_complet_debit = round(total_complet_debit, 2)
                total_complet_credit = round(total_complet_credit, 2)
                if float(total_complet_debit) != convert_montant(dataFame_sortie["Débit"][index]):
                    message = f"{message}Le total des débits ({float(total_complet_debit)}) " \
                              f"n'est pas égale au total du grand livre " \
                              f"({convert_montant(dataFame_sortie['Débit'][index])}) \n"
                if float(total_complet_credit) != convert_montant(dataFame_sortie["Crédit"][index]):
                    message = f"{message}Le total des crédits ({total_complet_credit}) " \
                              f"n'est pas égale au total du grand livre ({dataFame_sortie['Crédit'][index]}) \n"
                if len(message) > 0:
                    dataFame_sortie['Message Débit/Crédit'][index] = message
                else:
                    dataFame_sortie['Message Débit/Crédit'][index] = 'OK'
            else:
                total_debit = total_debit + convert_montant(dataFame_sortie['Débit'][index])
                total_credit = total_credit + convert_montant(dataFame_sortie['Crédit'][index])
    fin_etape_4 = datetime.today()
    print(f"Fin de l'étape 4 (vérification des totaux) à {fin_etape_4} pour une durée de {fin_etape_4 - fin_etape_3}")
    # Ecriture du dataframe de sortie
    dataFame_sortie.to_csv(f"Grand_livre.csv", sep=';', encoding='ANSI', decimal=",", index=False)
    return dataFame_sortie


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


def zero_if_empty(montant):
    if montant == '':
        return '0,00'
    else:
        return montant


def convert_montant(montant):
    return float(montant.replace(',', '.').replace(' ', ''))

if __name__ == '__main__':
    main()
