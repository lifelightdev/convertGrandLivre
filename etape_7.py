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
    df_piece, nb_ligne_piece = creer_piece()
    taille_tresorerie = 0

    for index in df_grand_livre.index:
        if existe_piece(piece):
            if change_piece(piece, df_grand_livre, index):
                if trouve_compte_banque(df_piece):
                    df_tresorerie, taille_tresorerie = ajoute_piece_dans_tresorerie(df_piece, df_tresorerie,
                                                                                    taille_tresorerie)
                df_piece.drop(df_piece.index, inplace=True)
                df_piece, nb_ligne_piece = creer_piece()
            df_piece.loc[nb_ligne_piece] = [df_grand_livre["Compte"][index],
                                            df_grand_livre["Intitulé du compte"][index], df_grand_livre["Pièce"][index],
                                            df_grand_livre["Date"][index], df_grand_livre["Journal"][index],
                                            df_grand_livre["Libellé"][index], df_grand_livre["Contre partie"][index],
                                            df_grand_livre["N° chèque"][index], df_grand_livre["Débit"][index],
                                            df_grand_livre["Crédit"][index], 0]
            nb_ligne_piece = nb_ligne_piece + 1
        piece = df_grand_livre['Pièce'][index]

    write_tresorerie(df_tresorerie, nom_syndic, date_impression, arrete_au)
    fin = datetime.today()
    print(f"Fin de l'étape 7 (Trésorerie) en {fin - debut}")


def creer_piece():
    df_piece = Entete_colonne
    nb_ligne_piece = 0
    return df_piece, nb_ligne_piece


def existe_piece(piece):
    return not (piece == '')


def change_piece(piece, df_grand_livre, index):
    return piece != df_grand_livre['Pièce'][index]


def piece_trouvee(nb_ligne_piece):
    return nb_ligne_piece > 0


def ajoute_piece_dans_tresorerie(df_piece, df_tresorerie, taille_tresorerie):
    new_tresorerie = df_tresorerie.copy()
    for index_piece in range(len(df_piece)):
        new_tresorerie.loc[taille_tresorerie] = [df_piece["Compte"][index_piece],
                                                 df_piece["Intitulé du compte"][index_piece],
                                                 df_piece["Pièce"][index_piece], df_piece["Date"][index_piece],
                                                 df_piece["Journal"][index_piece], df_piece["Libellé"][index_piece],
                                                 df_piece["Contre partie"][index_piece],
                                                 df_piece["N° chèque"][index_piece], df_piece["Débit"][index_piece],
                                                 df_piece["Crédit"][index_piece],
                                                 calcul_solde(len(df_tresorerie), index_piece)]
        taille_tresorerie = taille_tresorerie + 1
    return new_tresorerie, taille_tresorerie


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
    worksheet.set_column('I:L', 13, number_format)

    for index in df_tresorerie.index:
        piece = df_tresorerie['Pièce'][index]
        if piece != df_tresorerie['Pièce'][index]:
            worksheet.set_row(index - 1, cell_format=cell_format)

    workbook.close()


def calcul_solde(debut, index_piece):
    if index_piece == 0 or debut == 0:
        return f'=I{(debut)}-J{(debut)}'
    else:
        return f'=K{(debut)}+I{(debut + 1)}-J{(debut + 1)}'
