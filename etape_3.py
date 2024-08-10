#########
# Création du fichier des comptes '461900', '462900' trié par copropriétaire
#########

from datetime import datetime
import pandas
from constante import COLUMNS_NAME_COMPTE_S, DOSSIER_SORTIE, TOTAL_COMPTE


def etape_3_file_compte_s(df_entre, nom_syndic, date_impression, liste_cpt_copro):
    debut = datetime.today()
    liste_compte_operation_courante = ('461900', '462900')
    df_operation_courante = df_entre.loc[df_entre['Compte'].isin(liste_compte_operation_courante)]
    df_operation_courante = df_operation_courante[df_operation_courante['Libellé'].isin(
        [TOTAL_COMPTE, 'Solde compte excédent', 'Solde compte insuffisance']) == False]
    df_operation_courante = df_operation_courante.sort_values('Libellé')

    df_copro = df_entre.loc[df_entre['Compte'].isin(liste_cpt_copro)]
    df_copro = df_copro[df_copro['Libellé'].isin(['Répartition sur Opérations courantes du 01/01/22 au 31/12/22'])]
    # Correction du nom du copropriétaire dans l'intituler du compte
    for index in df_copro.index:
        df_copro['Intitulé du compte'][index] = delete_civilite(df_copro["Intitulé du compte"][index])
    df_copro = df_copro.sort_values('Intitulé du compte')

    df_sortie = pandas.DataFrame(columns=COLUMNS_NAME_COMPTE_S)

    nb_ligne_sortie = 0
    libelle = ''
    index_debut = 0
    total_solde = ''
    for index in df_operation_courante.index:
        if libelle == '':
            libelle = nom_coproprietaire(df_operation_courante['Libellé'][index])
            index_debut = nb_ligne_sortie + 2
        if libelle == nom_coproprietaire(df_operation_courante['Libellé'][index]):
            df_sortie.loc[nb_ligne_sortie] = [df_operation_courante["Compte"][index],
                                              df_operation_courante["Intitulé du compte"][index],
                                              df_operation_courante["Pièce"][index],
                                              df_operation_courante["Date"][index],
                                              df_operation_courante["Journal"][index],
                                              df_operation_courante["Libellé"][index],
                                              df_operation_courante["N° facture"][index],
                                              df_operation_courante["Débit"][index],
                                              df_operation_courante["Crédit"][index], ""]
        else:
            df_sortie.loc[nb_ligne_sortie] = [df_operation_courante['Compte'][index], f"{libelle}", "", "", "",
                                              "Total du copropriétaire", "",
                                              f"=SUM(H{index_debut}:H{nb_ligne_sortie + 1})",
                                              f"=SUM(I{index_debut}:I{nb_ligne_sortie + 1})",
                                              f"=I{(nb_ligne_sortie + 2)}-H{(nb_ligne_sortie + 2)}"]
            total_solde = f"{total_solde}+J{(nb_ligne_sortie + 2)}"
            nb_ligne_sortie = nb_ligne_sortie + 1

            # Recherche du copropriétaire
            for i in df_copro.index:
                intitule_cpt = df_copro["Intitulé du compte"][i]
                liste_mot_libelle = df_sortie['Libellé'][nb_ligne_sortie - 2].split(' ')
                liste_mot_libelle_intitule_cpt = intitule_cpt.split(' ')
                if liste_mot_libelle[0] == liste_mot_libelle_intitule_cpt[0]:
                    print(f"Le nom {liste_mot_libelle[0]} a été trouvé")
                    df_sortie.loc[nb_ligne_sortie] = [df_copro["Compte"][i],
                                                      df_copro["Intitulé du compte"][i],
                                                      df_copro["Pièce"][i],
                                                      df_copro["Date"][i],
                                                      df_copro["Journal"][i],
                                                      df_copro["Libellé"][i],
                                                      df_copro["N° facture"][i],
                                                      df_copro["Débit"][i],
                                                      df_copro["Crédit"][i],
                                                      f"=I{(nb_ligne_sortie + 2)}-H{(nb_ligne_sortie + 2)}"]
                    nb_ligne_sortie = nb_ligne_sortie + 1
                    df_copro = df_copro.drop([i])
                    break

            df_sortie.loc[nb_ligne_sortie] = [df_operation_courante["Compte"][index],
                                              df_operation_courante["Intitulé du compte"][index],
                                              df_operation_courante["Pièce"][index],
                                              df_operation_courante["Date"][index],
                                              df_operation_courante["Journal"][index],
                                              df_operation_courante["Libellé"][index],
                                              df_operation_courante["N° facture"][index],
                                              df_operation_courante["Débit"][index],
                                              df_operation_courante["Crédit"][index], ""]
            libelle = nom_coproprietaire(df_operation_courante['Libellé'][index])
            index_debut = nb_ligne_sortie + 2
        nb_ligne_sortie = nb_ligne_sortie + 1
    df_sortie.loc[nb_ligne_sortie] = [df_sortie['Compte'][nb_ligne_sortie - 1], libelle, "", "", "",
                                      "Total du copropriétaire", "", f"=SUM(H{index_debut}:H{nb_ligne_sortie + 1})",
                                      f"=SUM(I{index_debut}:I{nb_ligne_sortie + 1})",
                                      f"=I{(nb_ligne_sortie + 2)}-H{(nb_ligne_sortie + 2)}"]
    total_solde = f"{total_solde}+J{(nb_ligne_sortie + 2)}"
    nb_ligne_sortie = nb_ligne_sortie + 1
    df_sortie.loc[nb_ligne_sortie] = ["", "", "", "", "", "Total des comptes 461900 et 462900", "",
                                      df_operation_courante['Débit'].sum(), df_operation_courante['Crédit'].sum(),
                                      f"=I{(nb_ligne_sortie + 2)}-H{(nb_ligne_sortie + 2)}"]
    nb_ligne_sortie = nb_ligne_sortie + 1
    df_sortie.loc[nb_ligne_sortie] = ["", "", "", "", "", "Cumule des soldes par copropriétaire", "", "", "",
                                      f"={total_solde[1:]}"]

    max_size_libelle = max(df_sortie['Libellé'].str.len())
    max_size_compte = max(df_sortie['Intitulé du compte'].str.len())

    writer = pandas.ExcelWriter(
        f"{DOSSIER_SORTIE}/{nom_syndic}/compte_461900_462900 de {nom_syndic} du {date_impression}.xlsx")
    df_sortie.to_excel(writer, 'Feuille1', header=True, index=False, index_label=None, freeze_panes=(1, 1))
    workbook = writer.book
    worksheet = writer.sheets['Feuille1']

    number_format = workbook.add_format({'num_format': '#,##0.00;[RED]-#,##0.00'})
    cell_format = workbook.add_format({'bold': True, 'num_format': '#,##0.00;[RED]-#,##0.00'})
    text_format = workbook.add_format({'num_format': '@'})
    worksheet.set_column('A:A', 13, text_format)  # Compte
    worksheet.set_column('B:B', max_size_compte)  # Intituleé du compte
    worksheet.set_column('C:C', 13)  # Piéce
    worksheet.set_column('D:D', 13)  # Date
    worksheet.set_column('E:E', 6)  # Journal
    worksheet.set_column('F:F', max_size_libelle)  # Libellé
    worksheet.set_column('G:G', 13)  # Facture
    worksheet.set_column('H:K', 13, number_format)

    for index in df_sortie.index:
        if (df_sortie["Libellé"][index] == "Total du copropriétaire") \
                or (df_sortie["Libellé"][index] == "Total des comptes 461900 et 462900"):
            worksheet.write_array_formula(f'H{index + 2}', f'{df_sortie["Débit"][index]}', cell_format, 2005)
            worksheet.write_array_formula(f'I{index + 2}', f'{df_sortie["Crédit"][index]}', cell_format, 2005)
            worksheet.write_array_formula(f'J{index + 2}', f'{df_sortie["Solde"][index]}', cell_format, 2005)
            worksheet.set_row(index + 1, cell_format=cell_format)
        if (df_sortie["Compte"][index].startswith("450")):
            worksheet.write_array_formula(f'J{index + 2}', f'{df_sortie["Solde"][index]}', cell_format, 2005)
            worksheet.set_row(index + 1, cell_format=cell_format)
        if df_sortie["Libellé"][index] == "Cumule des soldes par copropriétaire":
            worksheet.write_array_formula(f'J{index + 2}', f'{df_sortie["Solde"][index]}', cell_format, 2005)
            worksheet.set_row(index + 1, cell_format=cell_format)
    writer.close()
    fin = datetime.today()
    print(f"Fin de l'étape 3 (Création du fichier des comptes 461900 et 462900 ) en {fin - debut}")


def delete_civilite(libelle):
    if libelle.startswith('M ou Mme '):
        libelle = libelle.replace('M ou Mme ', '')
    if libelle.startswith('M et Mme '):
        libelle = libelle.replace('M et Mme ', '')
    if libelle.startswith('M.'):
        libelle = libelle.replace('M. ', '')
    if libelle.startswith('M/Mme '):
        libelle = libelle.replace('M/Mme ', '')
    if libelle.startswith('M ET MME '):
        libelle = libelle.replace('M ET MME ', '')
    if libelle.startswith('M ET MME '):
        libelle = libelle.replace('M ET MME ', '')
    if libelle.startswith('MME '):
        libelle = libelle.replace('MME ', '')
    if libelle.startswith('MR / MME '):
        libelle = libelle.replace('MR / MME ', '')
    if libelle.startswith('Melle '):
        libelle = libelle.replace('Melle ', '')
    if libelle.startswith('Mme '):
        libelle = libelle.replace('Mme ', '')
    if libelle.startswith('Mme/'):
        libelle = libelle.replace('Mme/', '')
    if libelle.startswith('Mmes '):
        libelle = libelle.replace('Mmes ', '')
    if libelle.startswith('Monsieur '):
        libelle = libelle.replace('Monsieur ', '')
    if libelle.startswith('M OU MME '):
        libelle = libelle.replace('M OU MME ', '')
    if libelle.startswith('STE '):
        libelle = libelle.replace('STE ', '')
    if libelle.startswith('Sté '):
        libelle = libelle.replace('Sté ', '')
    if libelle.startswith('IND. '):
        libelle = libelle.replace('IND. ', '')
    if libelle.startswith('INDIVIS. '):
        libelle = libelle.replace('INDIVIS. ', '')
    if libelle.startswith('Ind '):
        libelle = libelle.replace('Ind ', '')
    if libelle.startswith('M '):
        libelle = libelle.replace('M ', '')
    return libelle


def nom_coproprietaire(libelle):
    if libelle is not None:
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
    return ""
