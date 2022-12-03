from datetime import datetime

import pandas

from constante import DOSSIER_ETAPE, SEPARATEUR_CSV, ENCODING, DECIMAL, COLUMNS_NAME
from outil import calcul_solde, convert_montant


def etape_6_journaux(etape, df_sortie):
    debut = datetime.today()
    if etape:
        df_sortie = pandas.read_csv(f"{DOSSIER_ETAPE}/Grand_livre.csv", sep=SEPARATEUR_CSV, encoding=ENCODING)
        df_sortie.columns = COLUMNS_NAME
    df_journaux = df_sortie.sort_values('Journal')
    journal = df_journaux.iloc[1]['Journal']
    index_nb_ligne_journal = 0
    df_journal = df_new_journal()
    for index in df_journaux.index:
        if journal != df_journaux["Journal"][index]:
            index_nb_ligne_journal, df_journal = add_total(df_journal, index_nb_ligne_journal)
            df_journaux.order
            write_journal(df_journal, index_nb_ligne_journal, journal)
            journal = df_journaux["Journal"][index]
            df_journal = df_new_journal()
            index_nb_ligne_journal = 0
        df_journal.loc[index_nb_ligne_journal] = [df_journaux["Compte"][index], df_journaux["Intitulé du compte"][index],
                                                  df_journaux["Pièce"][index], df_journaux["Date"][index],
                                                  df_journaux["Journal"][index], df_journaux["Libellé"][index],
                                                  df_journaux["N° facture"][index],
                                                  convert_montant(df_journaux["Débit"][index]),
                                                  convert_montant(df_journaux["Crédit"][index]),
                                                  calcul_solde(index_nb_ligne_journal)]
        index_nb_ligne_journal = index_nb_ligne_journal + 1
    df_journaux.to_csv(f"{DOSSIER_ETAPE}/journaux.csv", sep=SEPARATEUR_CSV, encoding=ENCODING, decimal=DECIMAL,
                       index=False)
    fin = datetime.today()
    print(f"Fin de l'étape 6 (Ecriture des journaux) en {fin - debut}")


def write_journal(df_journal, index_nb_ligne_journal, journal):
    max_size_libelle = max(df_journal['Libellé'].str.len())
    max_size_compte = max(df_journal['Intitulé du compte'].str.len())
    df_journal.to_csv(f"{DOSSIER_ETAPE}/journal_{journal}.csv", sep=SEPARATEUR_CSV, encoding=ENCODING, decimal=DECIMAL,
                      index=False)
    writer = pandas.ExcelWriter(f"Sortie/journal_{journal}.xlsx")
    df_journal.to_excel(writer, 'Feuille1', encoding=ENCODING, header=True, index=False, index_label=None,
                        freeze_panes=(1, 1))
    workbook = writer.book
    worksheet = writer.sheets['Feuille1']
    number_format = workbook.add_format({'num_format': '#,##0.00;[RED]-#,##0.00'})
    cell_format = workbook.add_format({'bold': True, 'num_format': '#,##0.00;[RED]-#,##0.00'})
    text_format = workbook.add_format({'num_format': '##0'})

    worksheet.set_column('A:A', 15, text_format)  # Compte
    worksheet.set_column('B:B', max_size_compte)  # Intitulé du compte
    worksheet.set_column('C:C', 13)  # Piéce
    worksheet.set_column('D:D', 13)  # Date
    worksheet.set_column('E:E', 10)  # Journal
    worksheet.set_column('F:F', max_size_libelle)  # Libellé
    worksheet.set_column('G:G', 13)  # Facture
    worksheet.set_column('H:J', 13, number_format)
    # Specify the result for a single cell range.
    for index in df_journal.index:
        if (df_journal["Libellé"][index] == "TOTAL DU JOURNAL"):
            worksheet.write_array_formula(f'H{index + 1}', f'{df_journal["Débit"][index]}', cell_format, 2005)
            worksheet.write_array_formula(f'I{index + 1}', f'{df_journal["Crédit"][index]}', cell_format, 2005)
            worksheet.set_row(index, cell_format=cell_format)
        if index < len(df_journal.index):
            worksheet.write_array_formula(f'J{index + 2}', f'{df_journal["Solde"][index]}', cell_format, 2005)
    writer.save()
    return df_journal, index_nb_ligne_journal, journal


def add_total(df_journal, index_nb_ligne_journal):
    index_nb_ligne_journal = index_nb_ligne_journal + 1
    df_journal.loc[index_nb_ligne_journal] = ["", "", "", "", "", "TOTAL DU JOURNAL", "",
                                              f"=SUM(H2:H{index_nb_ligne_journal})",
                                              f"=SUM(I2:I{index_nb_ligne_journal})",
                                              ""]
    return index_nb_ligne_journal, df_journal


def df_new_journal():
    return pandas.DataFrame(
        columns=["Compte", "Intitulé du compte", "Pièce", "Date", "Journal", "Libellé", "N° facture", "Débit", "Crédit",
                 "Solde"])
