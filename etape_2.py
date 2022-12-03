from datetime import datetime
import pandas
from extract_file import extract_nombre_de_page, extract_page_in_file
from extract_table import extract_total, extact_total_grand_livre, extact_total_montant
from constante import PATTERN_PIECE, SEPARATEUR_CSV, ENCODING, DECIMAL, DOSSIER_ETAPE, COLUMNS_NAME
from outil import convert_montant


def etape_2_create_df(etape, file_name, liste_compte):
    debut = datetime.today()
    if etape == 'True':
        df_sortie = pandas.read_csv(f"{DOSSIER_ETAPE}/Etape_2_Grand_livre_sans_compte.csv", sep=SEPARATEUR_CSV,
                                    encoding=ENCODING, decimal=DECIMAL)
        for index in df_sortie.index:
            df_sortie['Compte'][index] = str(df_sortie['Compte'][index]).replace('.0', '')
    else:
        # Création du dataframe de sortie
        df_sortie = pandas.DataFrame(columns=COLUMNS_NAME)
        nb_ligne_sortie = 1
        for nb in range(extract_nombre_de_page(file_name)):
            file = extract_page_in_file(file_name, nb)
            for i in range(0, len(file)):
                for j in range(0, len(file[i])):
                    if file[i][j] != ['Pièce/F/L', 'Date Cpt', 'Jal', 'L.', 'Libellé', 'N° Facture', 'Débit', 'Crédit',
                                      'Solde Débit', 'Solde Crédit']:
                        if not ligne_null(file[i][j]):
                            if len(file[i][j]) == 10:
                                if extract_total(file[i][j]):
                                    nb_ligne_sortie, solde_crebit, solde_debit = ajout_ligne_total(df_sortie, file, i,
                                                                                                   j, liste_compte,
                                                                                                   nb_ligne_sortie, 9)
                                else:
                                    df_sortie.loc[nb_ligne_sortie] = ["", "", file[i][j][0], file[i][j][1],
                                                                      file[i][j][2], file[i][j][4], file[i][j][5],
                                                                      zero_if_empty(file[i][j][6]),
                                                                      zero_if_empty(file[i][j][7]),
                                                                      zero_if_empty(file[i][j][8]),
                                                                      zero_if_empty(file[i][j][9]), "", ""]
                                    nb_ligne_sortie = nb_ligne_sortie + 1
                            elif len(file[i][j]) == 11:
                                if PATTERN_PIECE.match(file[i][j][0]) is None:
                                    df_sortie.loc[nb_ligne_sortie] = ["", "", file[i][j][0], file[i][j][1],
                                                                      file[i][j][2], file[i][j][4], file[i][j][5],
                                                                      zero_if_empty(file[i][j][7]),
                                                                      zero_if_empty(file[i][j][8]),
                                                                      zero_if_empty(file[i][j][9]),
                                                                      zero_if_empty(file[i][j][10]), "", ""]
                                    nb_ligne_sortie = nb_ligne_sortie + 1
                            elif len(file[i][j]) == 12:
                                if file[i][j][0].startswith('Total Général du Grand-Livre', 0, 28):
                                    montant = extact_total_grand_livre(file[i][j][0])
                                    df_sortie.loc[nb_ligne_sortie] = ["", "", "", "", "",
                                                                      "Total Général du Grand-Livre", "",
                                                                      zero_if_empty(montant[0]),
                                                                      zero_if_empty(montant[1]),
                                                                      zero_if_empty(montant[2]),
                                                                      zero_if_empty(file[i][j][-1]), "", ""]
                                    nb_ligne_sortie = nb_ligne_sortie + 1
                                else:
                                    if PATTERN_PIECE.match(file[i][j][0]) is not None:
                                        df_sortie.loc[nb_ligne_sortie] = ["", "", file[i][j][0], file[i][j][1],
                                                                          file[i][j][2], file[i][j][4], file[i][j][5],
                                                                          zero_if_empty(file[i][j][-4]),
                                                                          zero_if_empty(file[i][j][-3]),
                                                                          zero_if_empty(file[i][j][-2]),
                                                                          zero_if_empty(file[i][j][-1]), "", ""]
                                        nb_ligne_sortie = nb_ligne_sortie + 1
                                    elif extract_total(file[i][j]):
                                        nb_ligne_sortie, solde_crebit, solde_debit = ajout_ligne_total(df_sortie, file,
                                                                                                       i, j,
                                                                                                       liste_compte,
                                                                                                       nb_ligne_sortie,
                                                                                                       -1)
                            if len(file[i][j]) == 2:
                                if extract_total(file[i][j]):
                                    nb_ligne_sortie, solde_crebit, solde_debit = ajout_ligne_total(df_sortie, file, i,
                                                                                                   j, liste_compte,
                                                                                                   nb_ligne_sortie, 1)
        # Ecriture du dataframe de sortie
        df_sortie.to_csv(f"{DOSSIER_ETAPE}/Etape_2_Grand_livre_sans_compte.csv", sep=SEPARATEUR_CSV, encoding=ENCODING,
                         decimal=DECIMAL, index=False)

    max_size_libelle = max(df_sortie['Libellé'].str.len())

    fin = datetime.today()
    print(f"Fin de l'étape 2 (la création du fichier) en {fin - debut}")
    return df_sortie, max_size_libelle

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
        return convert_montant('0,00')
    else:
        return convert_montant(montant)

def ajout_ligne_total(df_sortie, file, i, j, liste_compte, nombre_de_ligne_sortie, id_solde_crebit):
    montant = extact_total_montant(file[i][j][0])
    if montant[0] not in liste_compte:
        libelle_compte = liste_compte[f"450{int(montant[0])}"]
        compte = f"450{int(montant[0])}"
    else:
        libelle_compte = liste_compte[montant[0]]
        compte = montant[0]
    df_sortie.loc[nombre_de_ligne_sortie] = [compte, libelle_compte, "", "", "", "TOTAL DU COMPTE", "",
                                             zero_if_empty(montant[1]), zero_if_empty(montant[2]),
                                             zero_if_empty(montant[3]), zero_if_empty(file[i][j][id_solde_crebit]), "",
                                             ""]
    nombre_de_ligne_sortie = nombre_de_ligne_sortie + 1
    return nombre_de_ligne_sortie, 0, 0
