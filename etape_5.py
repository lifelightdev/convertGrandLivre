#########
# Ecriture du fichier du grand livre
#########

from datetime import datetime
import pandas
from constante import DOSSIER_SORTIE, COPRO_S, COPRO_N, TOTAL_COMPTE
from outil import find_ligne_total


def etape_5_write_file_grand_livre(df_sortie, date_impression, nom_syndic, arrete_au, copro):
    debut = datetime.today()
    max_size_libelle = max(df_sortie['Libellé'].str.len())
    max_size_compte = max(df_sortie['Intitulé du compte'].str.len())
    if copro == COPRO_S:
        ids_ligne_totaux = find_ligne_total(df_sortie, TOTAL_COMPTE, "Total Général du Grand-Livre")
    if copro == COPRO_N:
        ids_ligne_totaux = find_ligne_total(df_sortie, TOTAL_COMPTE, "Total immeuble")
    writer = pandas.ExcelWriter(f"{DOSSIER_SORTIE}/{nom_syndic}/{date_impression} Grand livre - {nom_syndic} arrêté "
                                f"au {arrete_au}.xlsx")
    df_sortie.to_excel(writer, 'Feuille1', header=True, index=False, index_label=None, freeze_panes=(1, 1))
    workbook = writer.book
    worksheet = writer.sheets['Feuille1']
    number_format = workbook.add_format({'num_format': '#,##0.00'})
    cell_format = workbook.add_format({'bold': True, 'num_format': '#,##0.00'})
    text_format = workbook.add_format({'num_format': '@'})
    for index in ids_ligne_totaux:
         worksheet.set_row(index, None, cell_format)
    worksheet.set_column('A:A', 15, text_format)  # Compte
    worksheet.set_column('B:B', max_size_compte)  # Intitulé du compte
    worksheet.set_column('C:C', 13)  # Piéce
    worksheet.set_column('D:D', 13)  # Date
    worksheet.set_column('E:E', 10)  # Journal
    worksheet.set_column('F:F', max_size_libelle)  # Libellé
    worksheet.set_column('G:G', 13)  # Facture
    worksheet.set_column('H:K', 13, number_format)  # Montants
    worksheet.set_column('L:L', 20, number_format)  # Solde débit
    worksheet.set_column('M:M', 20, number_format)  # Solde crédit
    workbook.close()

    fin = datetime.today()
    print(f"Fin de l'étape 5 (écriture du fichier excel du grand livre) en {fin - debut}")
    return df_sortie
