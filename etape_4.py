from datetime import datetime
import pandas
from constante import COLUMNS_NAME_COMPTE, DOSSIER_ETAPE, SEPARATEUR_CSV, ENCODING, DECIMAL


def etape_4_extract_compte(df_entre):
    debut = datetime.today()
    df = df_entre.loc[df_entre['Compte'].isin(['461900', '462900'])]
    df = df[df['Libellé'].isin(['TOTAL DU COMPTE', 'Solde compte excédent', 'Solde compte insuffisance']) == False]
    df = df.sort_values('Libellé')
    df_sortie = pandas.DataFrame(columns=COLUMNS_NAME_COMPTE)
    nb_ligne_sortie = 0
    libelle = ''
    index_debut = 0
    total_solde = ''
    for index in df.index:
        if libelle == '':
            libelle = nom_coproprietaire(df['Libellé'][index])
            index_debut = nb_ligne_sortie + 2
        if libelle == nom_coproprietaire(df['Libellé'][index]):
            df_sortie.loc[nb_ligne_sortie] = [df["Compte"][index], df["Intitulé du compte"][index], df["Pièce"][index],
                                              df["Date"][index], df["Journal"][index], df["Libellé"][index],
                                              df["N° facture"][index], df["Débit"][index], df["Crédit"][index], ""]
        else:
            df_sortie.loc[nb_ligne_sortie] = [df['Compte'][index], f"{libelle}", "", "", "", "Total du copropriétaire",
                                              "", f"=SUM(H{index_debut}:H{nb_ligne_sortie + 1})",
                                              f"=SUM(I{index_debut}:I{nb_ligne_sortie + 1})",
                                              f"=I{(nb_ligne_sortie + 2)}-H{(nb_ligne_sortie + 2)}"]
            total_solde = f"{total_solde}+J{(nb_ligne_sortie + 2)}"
            nb_ligne_sortie = nb_ligne_sortie + 1
            df_sortie.loc[nb_ligne_sortie] = [df["Compte"][index], df["Intitulé du compte"][index], df["Pièce"][index],
                                              df["Date"][index], df["Journal"][index], df["Libellé"][index],
                                              df["N° facture"][index], df["Débit"][index], df["Crédit"][index], ""]
            libelle = nom_coproprietaire(df['Libellé'][index])
            index_debut = nb_ligne_sortie + 2
        nb_ligne_sortie = nb_ligne_sortie + 1
    df_sortie.loc[nb_ligne_sortie] = [df_sortie['Compte'][nb_ligne_sortie - 1], libelle, "", "", "",
                                      "Total du copropriétaire", "", f"=SUM(H{index_debut}:H{nb_ligne_sortie + 1})",
                                      f"=SUM(I{index_debut}:I{nb_ligne_sortie + 1})",
                                      f"=I{(nb_ligne_sortie + 2)}-H{(nb_ligne_sortie + 2)}"]
    total_solde = f"{total_solde}+J{(nb_ligne_sortie + 2)}"
    nb_ligne_sortie = nb_ligne_sortie + 1
    df_sortie.loc[nb_ligne_sortie] = ["", "", "", "", "", "Total des comptes 461900 et 462900", "",
                                      df['Débit'].sum(), df['Crédit'].sum(),
                                      f"=I{(nb_ligne_sortie + 2)}-H{(nb_ligne_sortie + 2)}"]
    nb_ligne_sortie = nb_ligne_sortie + 1
    df_sortie.loc[nb_ligne_sortie] = ["", "", "", "", "", "Cumule des soldes par copropriétaire", "", "", "",
                                      f"={total_solde[1:]}"]

    df_sortie.to_csv(f"{DOSSIER_ETAPE}/Etape_4_compte_461900df_461900_462900.csv", sep=SEPARATEUR_CSV,
                            encoding=ENCODING, decimal=DECIMAL, index=False)
    max_size_libelle = max(df_sortie['Libellé'].str.len())
    max_size_compte = max(df_sortie['Intitulé du compte'].str.len())

    writer = pandas.ExcelWriter(f"Sortie/compte_461900_462900.xlsx")
    df_sortie.to_excel(writer, 'Feuille1', encoding=ENCODING, header=True, index=False, index_label=None,
                       freeze_panes=(1, 1))
    workbook = writer.book
    worksheet = writer.sheets['Feuille1']

    number_format = workbook.add_format({'num_format': '#,##0.00;[RED]-#,##0.00'})
    cell_format = workbook.add_format({'bold': True, 'num_format': '#,##0.00;[RED]-#,##0.00'})
    text_format = workbook.add_format({'num_format': '@'})
    worksheet.set_column('A:A', 10, text_format)  # Compte
    worksheet.set_column('B:B', max_size_compte)  # Intituleé du compte
    worksheet.set_column('C:C', 13)  # Piéce
    worksheet.set_column('D:D', 13)  # Date
    worksheet.set_column('E:E', 6)  # Journal
    worksheet.set_column('F:F', max_size_libelle)  # Libellé
    worksheet.set_column('G:G', 13)  # Facture
    worksheet.set_column('H:I', 13, number_format)

    # Specify the result for a single cell range.
    for index in df_sortie.index:
        if (df_sortie["Libellé"][index] == "Total du copropriétaire") \
                or (df_sortie["Libellé"][index] == "Total des comptes 461900 et 462900"):
            worksheet.write_array_formula(f'H{index + 2}', f'{df_sortie["Débit"][index]}', cell_format, 2005)
            worksheet.write_array_formula(f'I{index + 2}', f'{df_sortie["Crédit"][index]}', cell_format, 2005)
            worksheet.write_array_formula(f'J{index + 2}', f'{df_sortie["Solde"][index]}', cell_format, 2005)
            worksheet.set_row(index + 1, cell_format=cell_format)
        if (df_sortie["Libellé"][index] == "Cumule des soldes par copropriétaire"):
            worksheet.write_array_formula(f'J{index + 2}', f'{df_sortie["Solde"][index]}', cell_format, 2005)
            worksheet.set_row(index + 1, cell_format=cell_format)
    writer.save()
    fin = datetime.today()
    print(f"Fin de l'étape 4 (Création du fichier des comptes 461900 et 462900 ) en {fin - debut}")


def nom_coproprietaire(libelle):
    nom = ''
    for index in libelle.split():
        if index == "Excédent":
            return nom
        elif index == "Insuffisance":
            return nom
        elif index == "au":
            return nom
        else:
            nom = f"{nom} {index}"
    return nom