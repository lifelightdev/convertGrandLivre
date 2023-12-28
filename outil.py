from datetime import datetime


def find_ligne_total(df, libelle_total_compte, libelle_total_grand_livre):
    ids_ligne_totaux = []
    for index in df.index:
        if df["Libellé"][index] is not None:
            if df["Libellé"][index].startswith(libelle_total_compte):
                ids_ligne_totaux.append(index + 1)
            if df["Libellé"][index].startswith(libelle_total_grand_livre):
                    ids_ligne_totaux.append(index + 1)
    return ids_ligne_totaux


def convert_montant(montant):
    return float(montant.replace('€','').replace(',', '.').replace(' ', ''))


def colums_name(nombre_de_colonne):
    liste_of_name_colums = []
    for x in range(0, nombre_de_colonne):
        liste_of_name_colums.append(f"{x}")
    return liste_of_name_colums


def nb_colonne(liste):
    nombre_de_colonne = 0
    for element in liste:
        if nombre_de_colonne < len(element):
            nombre_de_colonne = len(element)
    return nombre_de_colonne


def find_debit(debit):
    if  debit is not None:
        if debit.find(' €') < 0:
            debit = ''
        else:
            debit = debit.translate({ord(i): None for i in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'})
    else:
        debit = ''
    return debit


def find_journal_contre_partie_num_cheque(df_fichier, index, page, libelle):
    if (df_fichier.iloc[page][index])[7] is not None and (df_fichier.iloc[page][index])[7] != '':
        journal = (df_fichier.iloc[page][index])[7]
        contre_partie = (df_fichier.iloc[page][index])[8]
        num_cheque = (df_fichier.iloc[page][index])[len(df_fichier.iloc[page][index]) - 10]
    elif len((df_fichier.iloc[page][index])[0].split()) > 6:
        test = (df_fichier.iloc[page][index])[0].split()
        journal = test[3]
        contre_partie = test[3]
        num_cheque = ''
    elif (df_fichier.iloc[page][index])[8] is not None and (df_fichier.iloc[page][index])[8] != '':
        journal = (df_fichier.iloc[page][index])[8]
        contre_partie = (df_fichier.iloc[page][index])[9]
        num_cheque = (df_fichier.iloc[page][index])[10]
        if num_cheque is None:
            if (df_fichier.iloc[page][index])[11] != libelle:
                num_cheque = (df_fichier.iloc[page][index])[11]
    else:
        journal = (df_fichier.iloc[page][index])[9]
        contre_partie = (df_fichier.iloc[page][index])[10]
        if (df_fichier.iloc[page][index])[11] is None:
            num_cheque = (df_fichier.iloc[page][index])[12]
        else:
            num_cheque = (df_fichier.iloc[page][index])[11]
        if journal is not None:
            if journal.isnumeric() and len(journal) > 2:
                journal = (df_fichier.iloc[page][index])[8]
                contre_partie = (df_fichier.iloc[page][index])[9]
                if num_cheque is None:
                    num_cheque = (df_fichier.iloc[page][index])[10]
        test_colum_12 = (df_fichier.iloc[page][index])[len(df_fichier.iloc[page][index]) - 12]
        if test_colum_12 is not None and test_colum_12 != '' and len(journal) != 2:
            if not test_colum_12.isnumeric() or len(test_colum_12) == 2:
                journal = test_colum_12
                contre_partie = (df_fichier.iloc[page][index])[len(df_fichier.iloc[page][index]) - 11]
                num_cheque = (df_fichier.iloc[page][index])[len(df_fichier.iloc[page][index]) - 9]
    if num_cheque == libelle:
        num_cheque = ''
    return journal, contre_partie, num_cheque


def extract_solde(solde):
    solde = solde.replace('(Solde ', '')
    solde = solde.replace(' €)', '')
    solde_debit_extract = 0.0
    solde_credit_extract = 0.0
    if solde.find('débiteur') >= 0:
        solde_debit_extract = solde.replace('débiteur', '')
        solde_debit_extract = solde_debit_extract.replace(':', '')
        solde_debit_extract = convert_montant(solde_debit_extract)
    if solde.find('créditeur') >= 0:
        solde_credit_extract = solde.replace('créditeur', '')
        solde_credit_extract = solde_credit_extract.replace(':', '')
        solde_credit_extract = solde_credit_extract.replace('-', '')
        solde_credit_extract = convert_montant(solde_credit_extract)
    return solde_credit_extract, solde_debit_extract


def add_line_total(df_fichier, df_sortie, index, nb_ligne_sortie, page, list_id_total, compte, total_compte_debit,
                   total_compte_credit, total_immeuble_debit, total_immeuble_credit):
    for index_total in list_id_total:
        total = (df_fichier.iloc[page][index])[0]
        if total is not None:
            if total.find('Total') >= 0 and (total.find('Total du mois (') < 0 or compte == '51220'):
                debit = extract_debit(df_fichier, index, page)
                credit = extract_credit(df_fichier, index, page)
                case_solde = ''
                if len(df_fichier.iloc[page][index]) == 5:
                    if (df_fichier.iloc[page][index])[0].find('Solde') >= 0:
                        case_solde = (df_fichier.iloc[page][index])[3]
                else:
                    if (df_fichier.iloc[page][index])[7] != None:
                        if (df_fichier.iloc[page][index])[7].find('Solde') >= 0:
                            case_solde = (df_fichier.iloc[page][index])[index_total + 7]
                    if (df_fichier.iloc[page][index])[6] != None and case_solde == '':
                        if (df_fichier.iloc[page][index])[6].find('Solde') >= 0:
                            case_solde = (df_fichier.iloc[page][index])[index_total + 6]
                    if (df_fichier.iloc[page][index])[8] != None and case_solde == '':
                        if (df_fichier.iloc[page][index])[8].find('Solde') >= 0:
                            case_solde = (df_fichier.iloc[page][index])[index_total + 8]
                solde_credit_extract, solde_debit_extract = extract_solde(case_solde)
                solde_debit, solde_crebit = calcul_solde(credit, debit)
                solde_crebit = round(solde_crebit, 2)
                solde_debit = round(solde_debit, 2)
                verification = ""
                if total.find('Total du mois (') < 0:
                    if solde_credit_extract != solde_crebit:
                        verification = f"{verification} Le solde crédit est faux (dans le PDF c'est " \
                                       f"{solde_credit_extract} le calcul donne {solde_crebit} "
                    if solde_debit_extract != solde_debit:
                        verification = f"{verification} Le solde débit est faux  (dans le PDF c'est " \
                                       f"{solde_debit_extract} le calcul donne {solde_debit}"
                    if total_compte_credit != total_compte_debit:
                        solde_total_compte = total_compte_debit - total_compte_credit
                        solde_total_compte = round(solde_total_compte, 2)
                        if solde_total_compte > 0:
                            if solde_total_compte != (solde_debit):
                                verification = f"{verification} Le total débit ({total_compte_debit}) n'est pas " \
                                               f"égale au total crédit ({total_compte_credit}) la différence est de " \
                                               f"{solde_total_compte} qui n'est pas égale au solde débit ({solde_debit})"
                        elif solde_total_compte < 0:
                            if solde_total_compte != (solde_crebit * -1):
                                verification = f"{verification} Le total débit ({total_compte_debit}) n'est pas égale" \
                                               f" au total crédit ({total_compte_credit}) la différence est de " \
                                               f"{solde_total_compte} qui n'est pas égale au solde crédit " \
                                               f"({solde_crebit * -1})"
                else:
                    verification = "Sans objet"
                if total.find('Total immeuble') >= 0:
                    total_immeuble_debit = round(total_immeuble_debit + total_compte_debit, 2)
                    total_immeuble_credit = round(total_immeuble_credit + total_compte_credit, 2)
                    if total_immeuble_debit != total_immeuble_credit:
                        verification = f"Le total de l'immeuble débit ({total_immeuble_debit}) n'est pas égale au " \
                                       f"total crédit de l'immeuble ({total_immeuble_credit}) la différence est de " \
                                       f"{round(total_immeuble_debit - total_immeuble_credit, 2)}"
                    else:
                        verification = "OK"
                if verification == "":
                    verification = "OK"
                df_sortie.loc[nb_ligne_sortie] = ['', '', '', '', '', total, '', '', debit, credit, solde_debit,
                                                  solde_crebit, verification]
                nb_ligne_sortie = nb_ligne_sortie + 1
                break
    return nb_ligne_sortie, df_sortie


def find_intitule_du_compte(df_fichier, index, page):
    intitule_du_compte = ''
    if (df_fichier.iloc[page][index])[5] != None:
        intitule_du_compte = (df_fichier.iloc[page][index])[5]
    if (df_fichier.iloc[page][index])[6] != None:
        intitule_du_compte = (df_fichier.iloc[page][index])[6]
    if (df_fichier.iloc[page][index])[7] != None:
        intitule_du_compte = intitule_du_compte + (df_fichier.iloc[page][index])[7]
    if (df_fichier.iloc[page][index])[8] != None:
        intitule_du_compte = intitule_du_compte + (df_fichier.iloc[page][index])[8]
    return intitule_du_compte


def extract_credit(df_fichier, index, page):
    credit = ((df_fichier.iloc[page][index])[len(df_fichier.iloc[page][index]) - 2]).replace('€', '')
    if credit != '':
        credit = convert_montant(credit)
    else:
        credit = 0.0
    return credit


def extract_debit(df_fichier, index, page):
    debit = find_debit((df_fichier.iloc[page][index])[len(df_fichier.iloc[page][index]) - 4])
    if debit == '' or debit == None:
        debit = find_debit((df_fichier.iloc[page][index])[len(df_fichier.iloc[page][index]) - 3])
    if debit != '' and debit != None:
        debit = debit.replace('€', '')
        debit = convert_montant(debit)
    else:
        debit = 0.0
    return debit


def calcul_solde(credit, debit):
    solde_debit = 0.0
    solde_credit = 0.0
    if (debit - credit) > 0:
        solde_credit = debit - credit
    elif (debit - credit) < 0:
        solde_debit = credit - debit
    return solde_credit, solde_debit


def find_libelle(df_fichier, index, page):
    liste_id_libelle = [8, 9]
    libelle = ''
    for id_libelle in liste_id_libelle:
        libelle = (df_fichier.iloc[page][index])[len(df_fichier.iloc[page][index]) - id_libelle]
        if libelle != None:
            break
    if libelle != None:
        libelle = libelle.replace('*', '')
    return libelle

def is_date(valeur):
    format = "%d/%m/%Y"
    try:
        return bool(datetime.strptime(valeur, format))
    except :
        return False


def is_ligne_du_tableau(ligne):
    if ligne[0] == '92140' or ligne[0] == '01.46.45.40.97' or ligne[0] == 'Pièce':
        return False
    if len(ligne) > 1:
        #  Ligne du libellé de compte
        if ligne[0] == '' and (not ligne[2] == None and ligne[2].isnumeric()) and isinstance(ligne[5], str):
            return True
        # Ligne de Report
        if ligne[0] == '' and ligne[1] == None and is_date(ligne[2]):
            return True
        # Ligne d'opération
        if ligne[0].isnumeric() or is_date(ligne[0]):
            return True
        if isinstance(ligne[0], str):
            text = ligne[0].split()
            if len(text) > 0:
                if is_date(text[0]):
                    return True
                if is_date(text[1]):
                    return True
        # Ligne total
        if len(ligne) == 22:
            if (not ligne[10] == None) and (not ligne[10] == '') and ligne[10].startswith('Total compte '):
                return True
    return False


def is_ligne_libelle_compte(text):
    return text[0] == '' and text[1] == None and not not text[2] and (text[3] == None or text[3] == '') \
           and (text[4] == '' or text[4] == None) and not not text[5] and text[6] == None \
           and text[7] == '' and text[8] == None and text[9] == None
