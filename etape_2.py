#########
# Création du dataframe du grand livre
#########

from datetime import datetime
import pandas
from constante import PATTERN_PIECE, COLUMNS_NAME_S, COPRO_S, COPRO_N, COLUMNS_NAME_N, TOTAL_COMPTE
from extract_table import extract_total
from outil import convert_montant, is_date, is_ligne_du_tableau, is_ligne_null


def etape_2_create_df(pages, liste_compte, copro):
    debut = datetime.today()
    if copro == COPRO_S:
        df_sortie = copro_s(pages, liste_compte)
    elif copro == COPRO_N:
        df_sortie = copro_n(pages, liste_compte)
    fin = datetime.today()
    print(f"Fin de l'étape 2 (la création du fichier) en {fin - debut}")
    return df_sortie


def is_not_header_line(ligne):
    if ligne != 'Pièce Date Compte Jal C-Partie N° chèque Libellé Débit Crédit':
        return True
    else:
        return False


def is_not_ligne_start_word(ligne):
    if (ligne.startswith('Total du mois ( ')
            or ligne.startswith('Grand Livre arrêté au ')):
        return False
    else:
        mots = ligne.split()
        if mots[0].isnumeric() and not is_date(mots[1]):
            return False
        else:
            return True


def copro_n(pages, liste_compte):
    df_sortie = pandas.DataFrame(columns=COLUMNS_NAME_N)
    nb_ligne_sortie = 0
    for page in pages:
        for ligne in page:
            if is_ligne_du_tableau(ligne):
                if is_date(ligne[2]):
                    piece = ligne[0]
                    compte = ligne[6]
                    journal = ligne[11]
                    contre_partie = ligne[12]
                    num_cheque = ligne[15]
                    if journal == ''or journal is None:
                        journal = ligne[12]
                        contre_partie = ligne[13]
                        num_cheque = ligne[16]
                    if journal == ''or journal is None:
                        journal = ligne[13]
                        contre_partie = ligne[14]
                        num_cheque = ligne[17]
                    libelle_du_compte = find_libelle_du_compte(compte, liste_compte)
                    libelle_ecriture = ligne[15:20]
                    libelle_ecriture = extract_libelle_ecriture(libelle_ecriture)
                    debit = zero_if_empty(ligne[len(ligne) - 7].replace('€', '').replace(' ', ''))
                    credit = zero_if_empty(ligne[len(ligne) - 5].replace('€', '').replace(' ', ''))
                    df_sortie.loc[nb_ligne_sortie] = [compte, libelle_du_compte, piece, ligne[2], journal,
                                                      libelle_ecriture, contre_partie, num_cheque, debit, credit, "",
                                                      "", "", ""]
                    nb_ligne_sortie = nb_ligne_sortie + 1
            else:
                if not is_ligne_null(ligne):
                    if ligne[13] is not None:
                        if ligne[13].startswith('Total compte '):
                            compte = ligne[13].replace('Total compte ', '')
                            debit = zero_if_empty(ligne[len(ligne) - 7])
                            credit = zero_if_empty(ligne[len(ligne) - 5])
                            if (ligne[20] is not None) and ligne[20].startswith('(Solde créditeur : -'):
                                solde_debit = zero_if_empty('')
                                solde_credit = zero_if_empty(ligne[20].replace('(Solde créditeur : -', '')
                                                                      .replace(')', ''))
                            if (ligne[20] is not None) and ligne[20].startswith('(Solde débiteur : '):
                                solde_debit =  zero_if_empty(ligne[20].replace('(Solde débiteur : ', '')
                                                                      .replace(')', ''))
                                solde_credit = zero_if_empty('')
                            df_sortie.loc[nb_ligne_sortie] = [compte, "", "", "", "", TOTAL_COMPTE, "", "", debit,
                                                              credit, solde_debit, solde_credit, "", ""]
                            nb_ligne_sortie = nb_ligne_sortie + 1
                        elif ligne[13].startswith('Total immeuble'):
                            debit = zero_if_empty(ligne[len(ligne) - 7])
                            credit = zero_if_empty(ligne[len(ligne) - 5])
                            solde_debit = zero_if_empty('')
                            solde_credit = zero_if_empty('')
                            df_sortie.loc[nb_ligne_sortie] = ["", "", "", "", "", "Total immeuble", "", "", debit,
                                                              credit, solde_debit, solde_credit, "", ""]
                            nb_ligne_sortie = nb_ligne_sortie + 1
                    elif ligne[14] is not None:
                        solde_debit = zero_if_empty('')
                        solde_credit = zero_if_empty('')
                        if ligne[14].startswith('Total compte '):
                            compte = ligne[14].replace('Total compte ', '')
                            debit = zero_if_empty(ligne[len(ligne) - 7])
                            credit = zero_if_empty(ligne[len(ligne) - 5])
                            if (ligne[21] is not None) and ligne[21].startswith('(Solde créditeur : -'):
                                solde_debit = zero_if_empty('')
                                solde_credit = zero_if_empty(ligne[21].replace('(Solde créditeur : -', '')
                                                                      .replace(')', ''))
                            if (ligne[21] is not None) and ligne[21].startswith('(Solde débiteur : '):
                                solde_debit =  zero_if_empty(ligne[21].replace('(Solde débiteur : ', '')
                                                                      .replace(')', ''))
                                solde_credit = zero_if_empty('')
                            df_sortie.loc[nb_ligne_sortie] = [compte, "", "", "", "", TOTAL_COMPTE, "", "", debit,
                                                              credit, solde_debit, solde_credit, "", ""]
                            nb_ligne_sortie = nb_ligne_sortie + 1
    return df_sortie

def extract_libelle_ecriture(libelle_ecriture):
    if len(libelle_ecriture) > 1:
        lib = ''
        for text in libelle_ecriture:
            if text is not None:
                lib = lib + ' ' + text
        libelle_ecriture = lib.lstrip()
    else:
        libelle_ecriture = ' '.join(libelle_ecriture)
    return libelle_ecriture


def find_libelle_du_compte(compte, liste_compte):
    value = liste_compte.get(compte)
    if value is None:
        value = liste_compte.get(compte[0:compte.find('-')])
        if value is None:
            # logging.error(
            #     f"value = {value} Le compte {compte[0:compte.find('-')]} n'a pas été trouvé dans la liste des libellés de compte. "
            #     f"Le Libellé a été remplacé par le compte {compte[0:3] + '00' + compte[compte.find('-')::]} ")
            value = liste_compte.get(compte[0:3] + '00' + compte[compte.find('-')::])
            return value
        else:
            # logging.error(
            #     f"value = {value} Le compte {compte} n'a pas été trouvé dans la liste des libellés de compte. "
            #     f"Le Libellé a été remplacé par le compte {compte[0:compte.find('-')]} ")
            return value
    else:
        return value


def copro_s(file, liste_compte):
    df_sortie = pandas.DataFrame(columns=COLUMNS_NAME_S)
    nb_ligne_sortie = 0
    compte = ''
    libelle_du_compte = ''
    for page in range(0, len(file)):
        for ligne in range(0, len(file[page])):
            if not est_entete_de_colonne(file, ligne, page):
                if est_ligne_libelle_compte(file, ligne, page):
                    if file[page][ligne][0].startswith('Compte : '):
                        colonne = file[page][ligne][0].replace('Compte : ', '')
                        if colonne.startswith('450 Copropriétaire : '):
                            colonne = colonne.replace('450 Copropriétaire : ', '')
                            compte = f"450{int(colonne.split()[0])}"
                            libelle_du_compte = colonne.replace(colonne.split()[0], '').lstrip()
                        else:
                            compte = colonne.split()[0]
                            libelle_du_compte = colonne.replace(compte, '').lstrip()
                else:
                    if not is_ligne_null(file[page][ligne]):
                        if len(file[page][ligne]) == 10:
                            if extract_total(file[page][ligne]):
                                nb_ligne_sortie = ajout_ligne_total(df_sortie, file[page][ligne], liste_compte,
                                                                    nb_ligne_sortie)
                            else:
                                nb_ligne_sortie = add_line(compte, df_sortie, libelle_du_compte,
                                                           file[page][ligne], nb_ligne_sortie)
                        elif len(file[page][ligne]) == 11:
                            if PATTERN_PIECE.match(file[page][ligne][0]) is None:
                                nb_ligne_sortie = add_line(compte, df_sortie, libelle_du_compte,
                                                           file[page][ligne], nb_ligne_sortie)
                        elif len(file[page][ligne]) == 12:
                            if PATTERN_PIECE.match(file[page][ligne][0]) is not None:
                                nb_ligne_sortie = add_line(compte, df_sortie, libelle_du_compte,
                                                           file[page][ligne], nb_ligne_sortie)
                            elif extract_total(file[page][ligne]):
                                nb_ligne_sortie = ajout_ligne_total(df_sortie, file[page][ligne], liste_compte,
                                                                    nb_ligne_sortie)
                        elif len(file[page][ligne]) == 13:
                            if (file[page][ligne][4] is not None
                                    and file[page][ligne][4].startswith('Total Général du Grand-Livre', 0, 28)):
                                df_sortie.loc[nb_ligne_sortie] = ["", "", "", "", "", "Total Général du Grand-Livre",
                                                                  "", zero_if_empty(file[page][ligne][-4]),
                                                                  zero_if_empty(file[page][ligne][-3]),
                                                                  zero_if_empty(file[page][ligne][-2]),
                                                                  zero_if_empty(file[page][ligne][-1]), "", ""]
                            elif extract_total(file[page][ligne]):
                                nb_ligne_sortie = ajout_ligne_total(df_sortie, file[page][ligne], liste_compte,
                                                                    nb_ligne_sortie)
                            else:
                                df_sortie.loc[nb_ligne_sortie] = [compte, libelle_du_compte, file[page][ligne][0],
                                                                  file[page][ligne][1], file[page][ligne][2],
                                                                  file[page][ligne][5], file[page][ligne][6],
                                                                  zero_if_empty(file[page][ligne][-4]),
                                                                  zero_if_empty(file[page][ligne][-3]),
                                                                  zero_if_empty(file[page][ligne][-2]),
                                                                  zero_if_empty(file[page][ligne][-1]), "", ""]
                            nb_ligne_sortie = nb_ligne_sortie + 1
    return df_sortie


def add_line(compte, df_sortie, libelle_du_compte, ligne, nb_ligne_sortie):
    df_sortie.loc[nb_ligne_sortie] = [compte, libelle_du_compte, ligne[0], ligne[1], ligne[2], ligne[4], ligne[5],
                                      zero_if_empty(ligne[-4]), zero_if_empty(ligne[-3]), zero_if_empty(ligne[-2]),
                                      zero_if_empty(ligne[-1]), "", ""]
    return nb_ligne_sortie + 1


def est_ligne_libelle_compte(file, ligne, page):
    return file[page][ligne][0] is not None and file[page][ligne][0].startswith('Compte : ')


def est_entete_de_colonne(file, ligne, page):
    return (file[page][ligne] == ['Pièce/F/L', 'Date Cpt', 'Jal', 'L.', 'Libellé', 'N° Facture', 'Débit', 'Crédit',
                                  'Solde Débit', 'Solde Crédit']
            or file[page][ligne] == ['Pièce/F/L', 'Date Cpt', 'Jal', 'L.', None, 'Libellé', None, 'N° Facture', None,
                                     'Débit', 'Crédit', 'Solde Débit', 'Solde Crédit'])


def zero_if_empty(montant):
    if montant == '' or montant is None or not montant.isnumeric():
        if not montant.isnumeric():
            if not montant.replace('.', '').replace('€', '').replace('-', '').replace(' ', '').isnumeric():
                return convert_montant('0,00')
            else:
                return convert_montant(montant)
    else:
        return convert_montant(montant)


def ajout_ligne_total(df_sortie, ligne, liste_compte, nombre_de_ligne_sortie):
    compte = ligne[0].split()[4]
    if compte not in liste_compte:
        if compte.isnumeric():
            libelle_compte = liste_compte[f"450{int(compte)}"]
            compte = f"450{int(compte)}"
    else:
        libelle_compte = liste_compte[compte]
    df_sortie.loc[nombre_de_ligne_sortie] = [compte, libelle_compte, "", "", "", TOTAL_COMPTE, "",
                                             zero_if_empty(ligne[-4]), zero_if_empty(ligne[-3]),
                                             zero_if_empty(ligne[-2]), zero_if_empty(ligne[-1]), "", ""]
    nombre_de_ligne_sortie = nombre_de_ligne_sortie + 1
    return nombre_de_ligne_sortie
