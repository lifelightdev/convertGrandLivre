import logging
from datetime import datetime
import pandas
from constante import PATTERN_PIECE, COLUMNS_NAME_S, COPRO_S, COPRO_N, COLUMNS_NAME_N
from extract_table import extract_total
from outil import convert_montant, is_date, is_ligne_du_tableau, find_debit


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
                (contre_partie, credit, date, debit, journal, libelle_ecriture, num_cheque, piece, solde_credit,
                 solde_debit) = init(ligne)
                if is_date(date):
                    compte = ligne[1]
                    libelle_du_compte = find_libelle_du_compte(compte, liste_compte)
                    libelle_ecriture = ligne[2::]
                    libelle_ecriture = extract_libelle_ecriture(libelle_ecriture)
                    debit = zero_if_empty(ligne[len(ligne) - 4].replace('€', ''))
                    credit = zero_if_empty(ligne[len(ligne) - 2].replace('€', ''))
                else:
                    date = ligne[1]
                    if is_date(date):
                        piece = ligne[0]
                        compte = ligne[2]
                        libelle_du_compte = find_libelle_du_compte(compte, liste_compte)
                        if len(ligne[3]) == 2:
                            journal = ligne[3]
                            contre_partie = ligne[4]
                            if not ligne[5].isupper():
                                num_cheque = ligne[5]
                                libelle_ecriture = ligne[6::]
                            else:
                                libelle_ecriture = ligne[5::]
                            libelle_ecriture = extract_libelle_ecriture(libelle_ecriture)
                            if (ligne[len(ligne) - 4] is not None) and (ligne[len(ligne) - 4]).endswith('€'):
                                debit = zero_if_empty(ligne[len(ligne) - 4].replace('€', ''))
                                credit = zero_if_empty(ligne[len(ligne) - 2].replace('€', ''))
                            else:
                                if ligne[len(ligne) - 2] == '':
                                    debit = zero_if_empty(ligne[len(ligne) - 3].replace('€', ''))
                                    credit = zero_if_empty('00,00')
                                else:
                                    debit = zero_if_empty('00,00')
                                    credit = zero_if_empty(ligne[len(ligne) - 2].replace('€', ''))
                        else:
                            if len(ligne[3]) > 2 and isinstance(ligne[3][0:2], str):
                                journal = ligne[3][0:2]
                                contre_partie = ligne[3][2::]
                                libelle_ecriture = ligne[4::]
                                libelle_ecriture = extract_libelle_ecriture(libelle_ecriture)
                                if (ligne[len(ligne) - 3] is not None) and (ligne[len(ligne) - 3]).endswith('€'):
                                    debit = zero_if_empty(ligne[len(ligne) - 3].replace('€', ''))
                                    credit = zero_if_empty('0,00')
                                if (ligne[len(ligne) - 2]).endswith('€'):
                                    debit = zero_if_empty('0,00')
                                    credit = zero_if_empty(ligne[len(ligne) - 2].replace('€', ''))
                                if (ligne[len(ligne) - 4] is not None) and (ligne[len(ligne) - 4]).endswith('€'):
                                    debit = zero_if_empty(ligne[len(ligne) - 4].replace('€', ''))
                                    credit = zero_if_empty('0,00')
                    else:
                        date = ligne[2]
                        if is_date(date):
                            piece = ligne[0]
                            compte = ligne[4]
                            libelle_du_compte = find_libelle_du_compte(compte, liste_compte)
                            if not (ligne[7] == '') and (ligne[7] is not None):
                                journal = ligne[7]
                                contre_partie = ligne[8]
                                if (ligne[9] is not None) and (not (ligne[9] == '')):
                                    num_cheque = ligne[9]
                            elif not ligne[8] == '':
                                journal = ligne[8]
                                contre_partie = ligne[9]
                                if (ligne[10] is not None) and (not (ligne[10] == '')):
                                    num_cheque = ligne[10]
                            elif not ligne[9] == '':
                                journal = ligne[9]
                                contre_partie = ligne[10]
                            if (ligne[len(ligne) - 1] is None
                                    and ligne[len(ligne) - 2] == ''
                                    and ligne[len(ligne) - 5] is not None):
                                libelle_ecriture = ligne[len(ligne) - 5]
                                debit = zero_if_empty(find_debit(ligne[len(ligne) - 3]))
                                credit = zero_if_empty('')
                            else:
                                if (ligne[11] is not None) and (not (ligne[11] == '')):
                                    num_cheque = ligne[11]
                                elif (ligne[12] is not None) and (not (ligne[12] == '')):
                                    if (len(ligne[12]) <= 4) and (not ligne[12] == 'EDF') or (
                                            ligne[12] == '000PREL'):
                                        num_cheque = ligne[12]
                                    elif ligne[12].isnumeric():
                                        num_cheque = ligne[12]
                                    else:
                                        libelle_ecriture = libelle_ecriture + ligne[12]
                                if ligne[11] is not None:
                                    libelle_ecriture = ligne[11]
                                    if libelle_ecriture == num_cheque:
                                        num_cheque = ''
                                if ligne[12] is not None:
                                    libelle_ecriture = libelle_ecriture + ligne[12]
                                if (ligne[13] is not None) and (not (ligne[13] == '')):
                                    libelle_ecriture = libelle_ecriture + ligne[13]
                                if (ligne[14] is not None) and (not (ligne[14] == '')) and (
                                        ligne[14].find(' €') < 1):
                                    libelle_ecriture = libelle_ecriture + ligne[14]
                                if ligne[len(ligne) - 4] is not None:
                                    debit = zero_if_empty(find_debit(ligne[len(ligne) - 4]))
                                else:
                                    debit = zero_if_empty(find_debit(ligne[len(ligne) - 3]))
                                credit = zero_if_empty(ligne[len(ligne) - 2].replace('€', ''))
                        else:
                            if ligne[10].startswith('Total compte '):
                                libelle_ecriture = ligne[10]
                                debit = zero_if_empty(ligne[len(ligne) - 4].replace('€', ''))
                                credit = zero_if_empty(ligne[len(ligne) - 2].replace('€', ''))
                                if ligne[15] == '(Solde : 0.00 €)':
                                    solde_debit = zero_if_empty('')
                                    solde_credit = zero_if_empty('')
                                if (ligne[15] is not None) and ligne[15].startswith('(Solde créditeur : -'):
                                    solde_debit = zero_if_empty('')
                                    solde_credit = zero_if_empty(ligne[15][21: -3])
                                if (ligne[15] is not None) and ligne[15].startswith('(Solde débiteur : '):
                                    solde_debit = zero_if_empty(ligne[15][18: -3])
                                    solde_credit = zero_if_empty('')
                                if ligne[17] == '(Solde : 0.00 €)':
                                    solde_debit = zero_if_empty('')
                                    solde_credit = zero_if_empty('')
                                if (ligne[17] is not None) and ligne[17].startswith('(Solde créditeur : -'):
                                    solde_debit = zero_if_empty('')
                                    solde_credit = zero_if_empty(ligne[17][20: -3])
                                if (ligne[17] is not None) and ligne[17].startswith('(Solde débiteur : '):
                                    solde_debit = zero_if_empty(ligne[17][18: -3])
                                    solde_credit = zero_if_empty('')
                df_sortie.loc[nb_ligne_sortie] = [compte, libelle_du_compte, piece, date, journal, libelle_ecriture,
                                                  contre_partie, num_cheque, debit, credit, solde_debit,
                                                  solde_credit, "", ""]
                nb_ligne_sortie = nb_ligne_sortie + 1
            else:
                (contre_partie, credit, date, debit, journal, libelle_ecriture, num_cheque, piece, solde_credit,
                 solde_debit) = init(ligne)
                if len(ligne) > 1 and (ligne[10] is not None):
                    if ligne[10].startswith('Total compte ') or ligne[10].startswith('Total immeuble'):
                        libelle_ecriture = ligne[10]
                        if (ligne[len(ligne) - 3] is not None) and (ligne[len(ligne) - 3]).endswith('€'):
                            debit = zero_if_empty(ligne[len(ligne) - 3].replace('€', ''))
                            credit = zero_if_empty(ligne[len(ligne) - 2].replace('€', ''))
                        elif (ligne[len(ligne) - 4] is not None) and (ligne[len(ligne) - 4]).endswith('€'):
                            debit = zero_if_empty(ligne[len(ligne) - 4].replace('€', ''))
                            credit = zero_if_empty(ligne[len(ligne) - 2].replace('€', ''))
                        if ligne[10].endswith('(Solde : 0.00 €)'):
                            solde_debit = zero_if_empty('')
                            solde_credit = zero_if_empty('')
                        if ligne[16].endswith('(Solde : 0.00 €)'):
                            solde_debit = zero_if_empty('')
                            solde_credit = zero_if_empty('')
                        if ligne[16].startswith('(Solde créditeur : -'):
                            solde_debit = zero_if_empty('')
                            solde_credit = zero_if_empty(ligne[16][20: -3])
                        if ligne[16].startswith('(Solde débiteur : '):
                            solde_debit = zero_if_empty(ligne[16][18: -3])
                            solde_credit = zero_if_empty('')
                        df_sortie.loc[nb_ligne_sortie] = ['', '', '', '', '', libelle_ecriture, '', '', debit, credit,
                                                          solde_debit, solde_credit, '', '']
                        nb_ligne_sortie = nb_ligne_sortie + 1
                if len(ligne) > 8 and (ligne[8] is not None):
                    if ligne[8].startswith('Total compte ') or ligne[8].startswith('Total immeuble'):
                        libelle_ecriture = ligne[8]
                        if ligne[8].startswith('Total compte '):
                            compte = ligne[8][13: len(ligne[8])]
                            libelle_du_compte = find_libelle_du_compte(compte, liste_compte)
                        if ligne[8] == 'Total immeuble':
                            compte = ''
                            libelle_du_compte = ''
                        if (ligne[len(ligne) - 2] is not None) and (ligne[len(ligne) - 2]).endswith('€'):
                            debit = zero_if_empty(ligne[len(ligne) - 3].replace('€', ''))
                            credit = zero_if_empty(ligne[len(ligne) - 2].replace('€', ''))
                        if (ligne[8].endswith('(Solde : 0.00 €)')
                                or ligne[15] == '(Solde : 0.00 €)'
                                or ligne[16] == '(Solde : 0.00 €)'):
                            solde_debit = zero_if_empty('')
                            solde_credit = zero_if_empty('')
                        if (ligne[14] is not None) and ligne[14].startswith('(Solde créditeur : -'):
                            solde_debit = zero_if_empty('')
                            solde_credit = zero_if_empty(ligne[14][20: -3])
                        if (ligne[14] is not None) and ligne[14].startswith('(Solde débiteur : '):
                            solde_debit = zero_if_empty(ligne[14][18: -3])
                            solde_credit = zero_if_empty('')
                        df_sortie.loc[nb_ligne_sortie] = [compte, libelle_du_compte, '', '', '', libelle_ecriture, '',
                                                          '', debit, credit, solde_debit, solde_credit, '', '']
                        nb_ligne_sortie = nb_ligne_sortie + 1
                elif len(ligne) > 9 and (ligne[9] is not None):
                    if ligne[9].startswith('Total compte ') or ligne[9].startswith('Total immeuble'):
                        libelle_ecriture = ligne[9]
                        if ligne[9].startswith('Total compte '):
                            compte = ligne[9][13: len(ligne[9])]
                            libelle_du_compte = find_libelle_du_compte(compte, liste_compte)
                        if ligne[9] == 'Total immeuble':
                            compte = ''
                            libelle_du_compte = ''
                        if (ligne[len(ligne) - 4] is not None) and (ligne[len(ligne) - 4]).endswith('€'):
                            debit = zero_if_empty(ligne[len(ligne) - 4].replace('€', ''))
                            credit = zero_if_empty(ligne[len(ligne) - 2].replace('€', ''))
                        if (ligne[9].endswith('(Solde : 0.00 €)')
                                or ligne[15] == '(Solde : 0.00 €)'
                                or ligne[16] == '(Solde : 0.00 €)'):
                            solde_debit = zero_if_empty('')
                            solde_credit = zero_if_empty('')
                        if (ligne[15] is not None) and ligne[15].startswith('(Solde créditeur : -'):
                            solde_debit = zero_if_empty('')
                            solde_credit = zero_if_empty(ligne[15][20: -3])
                        if (ligne[15] is None) and ligne[15].startswith('(Solde débiteur : '):
                            solde_debit = zero_if_empty(ligne[15][18: -3])
                            solde_credit = zero_if_empty('')
                        df_sortie.loc[nb_ligne_sortie] = [compte, libelle_du_compte, '', '', '', libelle_ecriture, '',
                                                          '', debit, credit, solde_debit, solde_credit, '', '']
                        nb_ligne_sortie = nb_ligne_sortie + 1
                    elif (ligne[10] is not None) and (
                            ligne[10].startswith('Total compte ') or ligne[10].startswith('Total immeuble ')):
                        libelle_ecriture = ligne[10]
                        if (ligne[len(ligne) - 4] is not None) and (ligne[len(ligne) - 4]).endswith('€'):
                            debit = zero_if_empty(ligne[len(ligne) - 4].replace('€', ''))
                            credit = zero_if_empty(ligne[len(ligne) - 2].replace('€', ''))
                        if ligne[9].endswith('(Solde : 0.00 €)') or ligne[15] == '(Solde : 0.00 €)':
                            solde_debit = zero_if_empty('')
                            solde_credit = zero_if_empty('')
                        if ligne[9].find(' (Solde créditeur : -'):
                            id_solde_crediteur = ligne[10].find(' (Solde créditeur : -')
                        if id_solde_crediteur > 0:
                            solde_debit = zero_if_empty('')
                            solde_credit = zero_if_empty(ligne[0][id_solde_crediteur + 21: -3])
                        id_solde_dediteur = ligne[9].find(' (Solde débiteur : ')
                        if id_solde_dediteur > 0:
                            solde_debit = zero_if_empty(ligne[0][id_solde_dediteur + 19: -3])
                            solde_credit = zero_if_empty('')
                        df_sortie.loc[nb_ligne_sortie] = ['', '', '', '', '', libelle_ecriture, '', '', debit, credit,
                                                          solde_debit, solde_credit, '', '']
                        nb_ligne_sortie = nb_ligne_sortie + 1
    return df_sortie


def find_not_name_journal(journal):
    return not (journal == '15') and not (journal == '20') and not (journal == 'AC') \
        and not (journal == 'BA') and not (journal == 'BQ') and not (journal == 'OD') \
        and not (journal == 'P2') and not (journal == 'P4') and not (journal == 'PR') \
        and not (journal == 'VI')


def init(ligne):
    date = ligne[0]
    journal = ''
    piece = ''
    contre_partie = ''
    num_cheque = ''
    debit = zero_if_empty('00,00')
    credit = zero_if_empty('00,00')
    solde_debit = ''
    solde_credit = ''
    libelle_ecriture = ''
    return contre_partie, credit, date, debit, journal, libelle_ecriture, num_cheque, piece, solde_credit, solde_debit


def extract_libelle_ecriture(libelle_ecriture):
    if len(libelle_ecriture) > 1:
        lib = ''
        for text in libelle_ecriture:
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
            logging.error(
                f"value = {value} Le compte {compte[0:compte.find('-')]} n'a pas été trouvé dans la liste des libellés de compte. "
                f"Le Libellé a été remplacé par le compte {compte[0:3] + '00' + compte[compte.find('-')::]} ")
            value = liste_compte.get(compte[0:3] + '00' + compte[compte.find('-')::])
            return value
        else:
            logging.error(
                f"value = {value} Le compte {compte} n'a pas été trouvé dans la liste des libellés de compte. "
                f"Le Libellé a été remplacé par le compte {compte[0:compte.find('-')]} ")
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
                    if not ligne_null(file[page][ligne]):
                        if len(file[page][ligne]) == 10:
                            if extract_total(file[page][ligne]):
                                ajout_ligne_total(df_sortie, file[page][ligne], liste_compte, nb_ligne_sortie)
                            else:
                                df_sortie.loc[nb_ligne_sortie] = [compte, libelle_du_compte, file[page][ligne][0],
                                                                  file[page][ligne][1], file[page][ligne][2],
                                                                  file[page][ligne][4], file[page][ligne][5],
                                                                  zero_if_empty(file[page][ligne][6]),
                                                                  zero_if_empty(file[page][ligne][7]),
                                                                  zero_if_empty(file[page][ligne][8]),
                                                                  zero_if_empty(file[page][ligne][9]), "", ""]
                            nb_ligne_sortie = nb_ligne_sortie + 1
                        elif len(file[page][ligne]) == 11:
                            if PATTERN_PIECE.match(file[page][ligne][0]) is None:
                                df_sortie.loc[nb_ligne_sortie] = [compte, libelle_du_compte, file[page][ligne][0],
                                                                  file[page][ligne][1], file[page][ligne][2],
                                                                  file[page][ligne][4], file[page][ligne][5],
                                                                  zero_if_empty(file[page][ligne][7]),
                                                                  zero_if_empty(file[page][ligne][8]),
                                                                  zero_if_empty(file[page][ligne][9]),
                                                                  zero_if_empty(file[page][ligne][10]), "", ""]
                                nb_ligne_sortie = nb_ligne_sortie + 1
                        elif len(file[page][ligne]) == 12:
                            if PATTERN_PIECE.match(file[page][ligne][0]) is not None:
                                df_sortie.loc[nb_ligne_sortie] = [compte, libelle_du_compte, file[page][ligne][0],
                                                                  file[page][ligne][1],
                                                                  file[page][ligne][2], file[page][ligne][4],
                                                                  file[page][ligne][5],
                                                                  zero_if_empty(file[page][ligne][-4]),
                                                                  zero_if_empty(file[page][ligne][-3]),
                                                                  zero_if_empty(file[page][ligne][-2]),
                                                                  zero_if_empty(file[page][ligne][-1]), "", ""]
                                nb_ligne_sortie = nb_ligne_sortie + 1
                            elif extract_total(file[page][ligne]):
                                ajout_ligne_total(df_sortie, file[page][ligne], liste_compte, nb_ligne_sortie)
                        elif (len(file[page][ligne]) == 13) and (file[page][ligne][0] != 'Pièce/F/L'):
                            if (file[page][ligne][4] is not None
                                    and file[page][ligne][4].startswith('Total Général du Grand-Livre', 0, 28)):
                                df_sortie.loc[nb_ligne_sortie] = ["", "", "", "", "", "Total Général du Grand-Livre",
                                                                  "", zero_if_empty(file[page][ligne][-4]),
                                                                  zero_if_empty(file[page][ligne][-3]),
                                                                  zero_if_empty(file[page][ligne][-2]),
                                                                  zero_if_empty(file[page][ligne][-1]), "", ""]
                                nb_ligne_sortie = nb_ligne_sortie + 1
                            elif extract_total(file[page][ligne]):
                                ajout_ligne_total(df_sortie, file[page][ligne], liste_compte, nb_ligne_sortie)
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


def est_ligne_libelle_compte(file, ligne, page):
    return file[page][ligne][0] is not None and file[page][ligne][0].startswith('Compte : ')


def est_entete_de_colonne(file, ligne, page):
    return (file[page][ligne] == ['Pièce/F/L', 'Date Cpt', 'Jal', 'L.', 'Libellé', 'N° Facture', 'Débit', 'Crédit',
                                  'Solde Débit', 'Solde Crédit'])


def ligne_null(ligne):
    if ['', '', '', None, '', '', ''] == ligne:
        return True
    if ['', '', '', '', '', '', '', '', '', ''] == ligne:
        return True
    if ['', '', '', '', '', None, '', None, '', '', '', ''] == ligne:
        return True
    if ['', '', '', '', None, '', None, '', None, '', '', '', ''] == ligne:
        return True
    if ['', None, None, None, None, None, '', '', '', ''] == ligne:
        return True
    if ['', None, None, None, None, None, None, None, None, '', '', '', ''] == ligne:
        return True
    if ['', None, None, None, None, None, None, None, None, ''] == ligne:
        return True
    if ['', None, None, None, None, None, None, None, None, None] == ligne:
        return True
    if ['', None, None, None, None, None, None, None, None, None, None, ''] == ligne:
        return True
    if ['', None, None, None, None, None, None, None, None, None, None, None] == ligne:
        return True
    if ['', None, None, None, None, None, None, None, None, None, None, None, None] == ligne:
        return True
    if ['', None, 'DEBITEUR', None, None, '0,00', None, '', None, None, None, None] == ligne:
        return True
    if ['', None, 'DEBITEUR', None, None, None, '0,00', None, '', None, None, None, None] == ligne:
        return True
    return False


def zero_if_empty(montant):
    if montant == '' or montant is None:
        return convert_montant('0,00')
    else:
        return convert_montant(montant)


def ajout_ligne_total(df_sortie, ligne, liste_compte, nombre_de_ligne_sortie):
    compte = ligne[0].split()[4]
    if compte not in liste_compte:
        if compte.isnumeric():
            libelle_compte = liste_compte[f"450{compte}"]
            compte = f"450{int(compte)}"
    else:
        libelle_compte = liste_compte[compte]
    df_sortie.loc[nombre_de_ligne_sortie] = [compte, libelle_compte, "", "", "", "TOTAL DU COMPTE", "",
                                             zero_if_empty(ligne[-4]), zero_if_empty(ligne[-3]),
                                             zero_if_empty(ligne[-2]), zero_if_empty(ligne[-1]), "", ""]
