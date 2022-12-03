from datetime import datetime
import pandas
from constante import DOSSIER_ETAPE, SEPARATEUR_CSV, ENCODING, DECIMAL, DOSSIER_SORTIE
from outil import find_ligne_total


def etape_5_total(df_sortie, max_size_compte, max_size_libelle):
    debut = datetime.today()
    total_debit = 0
    total_credit = 0
    total_complet_debit = 0
    total_complet_credit = 0
    compte = df_sortie["Compte"][1]
    print(f"compte = {compte}")
    message = ''
    for index in df_sortie.index:
        if compte == df_sortie["Compte"][index]:
            if df_sortie["Libellé"][index] == "TOTAL DU COMPTE":
                compte, total_complet_credit, total_complet_debit, total_credit, total_debit = verif_totaux_compte(
                    df_sortie, index, total_complet_credit, total_complet_debit, total_credit, total_debit)
                if total_debit > total_credit:
                    if df_sortie["Solde Débit"][index] == (total_debit - total_credit):
                        message = 'OK'
                    else:
                        message = f"Solde des débits ({float(total_debit - total_credit)}) n'est pas égale au solde " \
                                  f"du grand livre = ({df_sortie['Solde Débit'][index]}) \n"
                if total_credit > total_debit:
                    if df_sortie["Solde Crédit"][index] != (total_credit - total_debit):
                        message = f"Solde des crédits ({float(total_credit - total_debit)}) n'est pas égale au solde " \
                                  f"du grand livre = ({df_sortie['Solde Crédit'][index]}) \n"
                if len(message) > 0:
                    df_sortie['Vérification Solde'][index] = message
                else:
                    df_sortie['Vérification Solde'][index] = 'OK'
            elif df_sortie["Libellé"][index] == 'Total Général du Grand-Livre':
                total_complet_credit, total_complet_debit = verif_totaux_grand_livre(df_sortie, index,
                                                                                     total_complet_credit,
                                                                                     total_complet_debit)
                if total_complet_debit > total_complet_credit:
                    if df_sortie["Solde Débit"][index] == (total_complet_debit - total_complet_credit):
                        message = 'OK'
                    else:
                        message = f"Solde général des débits ({float(total_complet_debit - total_complet_credit)}) " \
                                  f"n'est pas égale au solde du grand livre = " \
                                  f"({df_sortie['Solde Débit'][index]}) \n"
                if total_complet_credit > total_complet_debit:
                    if df_sortie["Solde Crédit"][index] != (total_complet_credit - total_complet_debit):
                        message = f"Solde général des crédits ({float(total_complet_credit - total_complet_debit)}) " \
                                  f"n'est pas égale au solde du grand livre = " \
                                  f"({df_sortie['Solde Crédit'][index]}) \n"
                if len(message) > 0:
                    df_sortie['Vérification Solde'][index] = message
                else:
                    df_sortie['Vérification Solde'][index] = 'OK'
            else:
                total_debit = total_debit + df_sortie['Débit'][index]
                total_credit = total_credit + df_sortie['Crédit'][index]
        else:
            compte = df_sortie["Compte"][index]

    # Ecriture du dataframe de sortie
    ids_ligne_totaux = find_ligne_total(df_sortie, "TOTAL DU COMPTE")
    df_sorties_copy = remove_compte_in_total(df_sortie, ids_ligne_totaux)
    max_size_Solde = max(df_sorties_copy['Vérification Solde'].str.len())
    max_size_Debit_Credit = max(df_sorties_copy['Vérification Débit/Crédit'].str.len())
    df_sorties_copy.to_csv(f"{DOSSIER_ETAPE}/Grand_livre.csv", sep=SEPARATEUR_CSV, encoding=ENCODING, decimal=DECIMAL,
                           index=False)
    writer = pandas.ExcelWriter(f"{DOSSIER_SORTIE}/Grand_livre.xlsx")
    df_sorties_copy.to_excel(writer, 'Feuille1', encoding=ENCODING, header=True, index=False, index_label=None,
                             freeze_panes=(1, 1))
    workbook = writer.book
    worksheet = writer.sheets['Feuille1']
    number_format = workbook.add_format({'num_format': '#,##0.00'})
    cell_format = workbook.add_format({'bold': True, 'num_format': '#,##0.00'})
    text_format = workbook.add_format({'num_format': '@'})
    for index in ids_ligne_totaux:
        worksheet.set_row(index, None, cell_format)
    worksheet.set_column('A:A', 15, text_format)  # Compte
    worksheet.set_column('B:B', max_size_compte)  # Intituleé du compte
    worksheet.set_column('C:C', 13)  # Piéce
    worksheet.set_column('D:D', 13)  # Date
    worksheet.set_column('E:E', 10)  # Journal
    worksheet.set_column('F:F', max_size_libelle)  # Libellé
    worksheet.set_column('G:G', 13)  # Facture
    worksheet.set_column('H:K', 13, number_format)  # Montants
    worksheet.set_column('L:L', max_size_Debit_Credit, number_format)  # Vérification Débit/Crédit
    worksheet.set_column('M:M', max_size_Solde, number_format)  # Vérification Solde
    writer.save()

    fin = datetime.today()
    print(f"Fin de l'étape 5 (vérification des totaux) en {fin - debut}")
    return df_sortie


def remove_compte_in_total(df_sortie, ids_ligne_totaux):
    for index in ids_ligne_totaux:
        df_sortie["Compte"][index] = ""
    return df_sortie


def verif_totaux_grand_livre(df_sortie, index, total_complet_credit, total_complet_debit):
    message = ''
    total_complet_debit = round(total_complet_debit, 2)
    total_complet_credit = round(total_complet_credit, 2)
    if float(total_complet_debit) != df_sortie["Débit"][index]:
        message = f"Le total des débits ({float(total_complet_debit)}) n'est pas égale au total du grand livre" \
                  f" ({df_sortie['Débit'][index]}) \n"
    if float(total_complet_credit) != df_sortie["Crédit"][index]:
        message = f"Le total des crédits ({total_complet_credit}) n'est pas égale au total du grand livre " \
                  f"({df_sortie['Crédit'][index]}) \n"
    if len(message) > 0:
        df_sortie['Vérification Débit/Crédit'][index] = message
    else:
        df_sortie['Vérification Débit/Crédit'][index] = 'OK'
    return total_complet_credit, total_complet_debit


def verif_totaux_compte(df_sortie, index, total_complet_credit, total_complet_debit, total_credit, total_debit):
    message = ''
    total_debit = round(float(total_debit), 2)
    total_credit = round(float(total_credit), 2)
    if float(total_debit) != df_sortie["Débit"][index]:
        message = f"Le total des débits ({float(total_debit)}) n'est pas égale au total du grand livre = " \
                  f"({df_sortie['Débit'][index]}) \n"
    if float(total_credit) != df_sortie["Crédit"][index]:
        message = f"Le total des crédits ({total_credit}) n'est pas égale au total du grand livre " \
                  f"({df_sortie['Crédit'][index]}) \n"
    if len(message) > 0:
        df_sortie['Vérification Débit/Crédit'][index] = message
    else:
        df_sortie['Vérification Débit/Crédit'][index] = 'OK'
    total_complet_debit = total_complet_debit + total_debit
    total_complet_credit = total_complet_credit + total_credit
    total_debit = 0
    total_credit = 0
    compte = df_sortie["Compte"][index + 1]
    return compte, total_complet_credit, total_complet_debit, total_credit, total_debit
