from datetime import datetime
import pandas
from constante import DOSSIER_SORTIE

Entete_colonne = pandas.DataFrame(
    columns=["Compte", "Intitulé du compte", "Pièce", "Date", "Journal", "Libellé", "Contre partie", "N° chèque",
             "Débit", "Crédit", "Solde"])


def etape_7_tresorerie(df_sortie, nom_syndic, date_impression, arrete_au):
    debut = datetime.today()
    df_grand_livre = df_sortie.sort_values('Pièce', ascending=True)
    piece = df_grand_livre.iloc[1]['Pièce']
    df_tresorerie = Entete_colonne
    df_piece = Entete_colonne

    for index in df_grand_livre.index:
        if existe_piece(piece):
            if change_piece(piece, df_grand_livre, index):
                if trouve_compte_banque(df_piece):
                    df_piece = df_piece.sort_values('Compte', ascending=True)
                    df_piece.loc[df_piece.size + 1] = ["", "", piece, "", "", "Total de la pièce", "", "", "-1", "-1",
                                                       "-1"]
                    df_piece.reset_index(drop=True, inplace=True)
                    df_tresorerie = pandas.concat([df_tresorerie, df_piece], ignore_index=True)
                    df_tresorerie.reset_index(drop=True, inplace=True)
                df_piece.drop(df_piece.index, inplace=True)
            df_piece.loc[df_piece.size + 1] = [df_grand_livre["Compte"][index],
                                               df_grand_livre["Intitulé du compte"][index],
                                               df_grand_livre["Pièce"][index],
                                               df_grand_livre["Date"][index], df_grand_livre["Journal"][index],
                                               df_grand_livre["Libellé"][index], df_grand_livre["Contre partie"][index],
                                               df_grand_livre["N° chèque"][index], df_grand_livre["Débit"][index],
                                               df_grand_livre["Crédit"][index], -1]
        piece = df_grand_livre['Pièce'][index]

    total_piece_debit = 0
    total_piece_credit = 0
    df_tresorerie.reset_index(drop=True, inplace=True)
    for i in df_tresorerie.index:
        df_tresorerie['Solde'][i] = calcul_solde(i)
        if df_tresorerie['Libellé'][i] == 'Total de la pièce':
            df_tresorerie['Débit'][i] = total_piece_debit
            df_tresorerie['Crédit'][i] = total_piece_credit
            total_piece_debit = 0
            total_piece_credit = 0
        else:
            total_piece_debit = float(total_piece_debit) + float(df_tresorerie['Débit'][i])
            total_piece_credit = float(total_piece_credit) + float(df_tresorerie['Crédit'][i])
    i = i + 1

    write_tresorerie(df_tresorerie, nom_syndic, date_impression, arrete_au)
    fin = datetime.today()
    print(f"Fin de l'étape 7 (Trésorerie) en {fin - debut}")


def existe_piece(piece):
    return piece != ''


def change_piece(piece, df_grand_livre, index):
    return piece != df_grand_livre['Pièce'][index]


def piece_trouvee(nb_ligne_piece):
    return nb_ligne_piece > 0


def trouve_compte_banque(df_piece):
    trouver_compte_banque = False
    for index_piece in df_piece.index:
        if df_piece['Compte'][index_piece].startswith('512') \
                or df_piece['Contre partie'][index_piece].startswith('512'):
            trouver_compte_banque = True
            break
    return trouver_compte_banque


def write_tresorerie(df_tresorerie, nom_syndic, date_impression, arrete_au):
    max_size_libelle = max(df_tresorerie['Libellé'].str.len())
    max_size_compte = max(df_tresorerie['Intitulé du compte'].str.len())
    writer = pandas.ExcelWriter(f"{DOSSIER_SORTIE}/{nom_syndic}/Tresorerie de {nom_syndic} en date du "
                                f"{date_impression} arrêté au {arrete_au}.xlsx")
    df_tresorerie.to_excel(writer, 'Feuille1', header=True, index=False, index_label=None, freeze_panes=(1, 1))
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
    worksheet.set_column('G:G', 13)  # Contre partie
    worksheet.set_column('H:H', 13)  # N° chèque
    worksheet.set_column('I:L', 13, number_format)  # I = Débit J = Crédit et K = Solde

    for index in df_tresorerie.index:
        if index > 0:
            worksheet.write_array_formula(f'K{index + 1}', f'{df_tresorerie["Solde"][index]}', number_format, 2005)
        if df_tresorerie['Libellé'][index] == 'Total de la pièce':
            worksheet.set_row(index + 1, cell_format=cell_format)

    workbook.close()


def calcul_solde(ligne):
    if ligne == 1:
        return f'=J{ligne + 1}-I{ligne + 1}'
    else:
        return f'=K{(ligne)}+J{ligne + 1}-I{ligne + 1}'
