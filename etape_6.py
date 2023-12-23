from datetime import datetime
import pandas
from constante import DOSSIER_SORTIE, COPRO_N


def etape_6_journaux(df_sortie, nom_syndic, date_impression, arrete_au, copro):
    debut = datetime.today()
    df_journaux = df_sortie.sort_values('Journal', ascending=False)
    journal = df_journaux.iloc[1]['Journal']
    index_nb_ligne_journal = 0
    df_journal = df_new_journal(copro)
    for index in df_journaux.index:
        if journal != df_journaux["Journal"][index]:
            index_nb_ligne_journal, df_journal = add_total(df_journal, index_nb_ligne_journal, copro)
            write_journal(df_journal, index_nb_ligne_journal, journal, nom_syndic, date_impression, arrete_au, copro)
            journal = df_journaux["Journal"][index]
            df_journal = df_new_journal(copro)
            index_nb_ligne_journal = 0
        if copro == COPRO_N:
            df_journal.loc[index_nb_ligne_journal] = [df_journaux["Compte"][index],
                                                      df_journaux["Intitulé du compte"][index],
                                                      df_journaux["Pièce"][index], df_journaux["Date"][index],
                                                      df_journaux["Journal"][index], df_journaux["Libellé"][index],
                                                      df_journaux["Contre partie"][index],
                                                      df_journaux["N° chèque"][index],
                                                      df_journaux["Débit"][index],
                                                      df_journaux["Crédit"][index],
                                                      calcul_solde(index_nb_ligne_journal, copro)]
        else:
            df_journal.loc[index_nb_ligne_journal] = [df_journaux["Compte"][index],
                                                      df_journaux["Intitulé du compte"][index],
                                                      df_journaux["Pièce"][index], df_journaux["Date"][index],
                                                      df_journaux["Journal"][index], df_journaux["Libellé"][index],
                                                      df_journaux["N° facture"][index], df_journaux["Débit"][index],
                                                      df_journaux["Crédit"][index],
                                                      calcul_solde(index_nb_ligne_journal, copro)]
        index_nb_ligne_journal = index_nb_ligne_journal + 1
    fin = datetime.today()
    print(f"Fin de l'étape 6 (Ecriture des journaux) en {fin - debut}")


def write_journal(df_journal, index_nb_ligne_journal, journal, nom_syndic, date_impression, arrete_au, copro):
    if not pandas.isna(journal):
        max_size_libelle = max(df_journal['Libellé'].str.len())
        max_size_compte = max(df_journal['Intitulé du compte'].str.len())
        writer = pandas.ExcelWriter(f"{DOSSIER_SORTIE}/{nom_syndic}/Journal {journal} de {nom_syndic} en date du "
                                    f"{date_impression} arrêté au {arrete_au}.xlsx")
        df_journal.to_excel(writer, 'Feuille1', header=True, index=False, index_label=None,
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
        if copro == COPRO_N:
            worksheet.set_column('G:G', 13)  # Contre partie
            worksheet.set_column('H:H', 13)  # N° chèque
            worksheet.set_column('I:L', 13, number_format)
        else :
            worksheet.set_column('G:G', 13)  # Facture
            worksheet.set_column('H:J', 13, number_format)
        for index in df_journal.index:
            if (df_journal["Libellé"][index] == "TOTAL DU JOURNAL"):
                if copro == COPRO_N:
                    worksheet.write_array_formula(f'I{index + 1}', f'{df_journal["Débit"][index]}', cell_format, 2005)
                    worksheet.write_array_formula(f'J{index + 1}', f'{df_journal["Crédit"][index]}', cell_format, 2005)
                else:
                    worksheet.write_array_formula(f'H{index + 1}', f'{df_journal["Débit"][index]}', cell_format, 2005)
                    worksheet.write_array_formula(f'I{index + 1}', f'{df_journal["Crédit"][index]}', cell_format, 2005)
                worksheet.set_row(index, cell_format=cell_format)
            if index < len(df_journal.index):
                if copro == COPRO_N:
                    worksheet.write_array_formula(f'K{index + 2}', f'{df_journal["Solde"][index]}', cell_format, 2005)
                else:
                    worksheet.write_array_formula(f'J{index + 2}', f'{df_journal["Solde"][index]}', cell_format, 2005)
        workbook.close()
    return df_journal, index_nb_ligne_journal, journal


def add_total(df_journal, index_nb_ligne_journal, copro):
    index_nb_ligne_journal = index_nb_ligne_journal + 1
    if copro == COPRO_N:
        df_journal.loc[index_nb_ligne_journal] = ["", "", "", "", "", "TOTAL DU JOURNAL", "", "",
                                                  f"=SUM(I2:I{index_nb_ligne_journal})",
                                                  f"=SUM(J2:J{index_nb_ligne_journal})", ""]
    else:
        df_journal.loc[index_nb_ligne_journal] = ["", "", "", "", "", "TOTAL DU JOURNAL", "",
                                                  f"=SUM(H2:H{index_nb_ligne_journal})",
                                                  f"=SUM(I2:I{index_nb_ligne_journal})", ""]
    return index_nb_ligne_journal, df_journal


def df_new_journal(copro):
    if copro == COPRO_N:
        return pandas.DataFrame(columns=["Compte", "Intitulé du compte", "Pièce", "Date", "Journal", "Libellé",
                                         "Contre partie", "N° chèque", "Débit", "Crédit", "Solde"])
    else:
        return pandas.DataFrame(columns=["Compte", "Intitulé du compte", "Pièce", "Date", "Journal", "Libellé",
                                         "N° facture", "Débit", "Crédit", "Solde"])


def calcul_solde(index_num_ligne, copro):
    if copro == COPRO_N:
        if index_num_ligne == 0:
            return f'=I{(index_num_ligne + 2)}-J{(index_num_ligne + 2)}'
        else:
            return f'=K{(index_num_ligne + 2) - 1}+J{(index_num_ligne + 2)}-I{(index_num_ligne + 2)}'
    else:
        if index_num_ligne == 0:
            return f'=I{(index_num_ligne + 2)}-H{(index_num_ligne + 2)}'
        else:
            return f'=J{(index_num_ligne + 2) - 1}+I{(index_num_ligne + 2)}-H{(index_num_ligne + 2)}'
