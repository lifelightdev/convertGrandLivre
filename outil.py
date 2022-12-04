def calcul_solde(index_num_ligne):
    if index_num_ligne == 0:
        return f'=I{(index_num_ligne + 2)}-H{(index_num_ligne + 2)}'
    else:
        return f'=J{(index_num_ligne + 2) - 1}+I{(index_num_ligne + 2)}-H{(index_num_ligne + 2)}'


def find_ligne_total(df, column_name):
    ids_ligne_totaux = []
    for index in df.index:
        if df["Libellé"][index] == column_name:
            ids_ligne_totaux.append(index)
    return ids_ligne_totaux


def convert_montant(montant):
    return float(montant.replace(',', '.').replace(' ', ''))


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
    if debit != None:
        if debit.find(' €') < 0:
            debit = ''
        else:
            debit = debit.translate({ord(i): None for i in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'})
    return debit


def find_journal_contre_partie_num_cheque(df_fichier, index, page):
    journal = (df_fichier.iloc[page][index])[9]
    contre_partie = (df_fichier.iloc[page][index])[10]
    num_cheque = (df_fichier.iloc[page][index])[11]
    if num_cheque is None:
        num_cheque = (df_fichier.iloc[page][index])[12]
    test_colum_12 = (df_fichier.iloc[page][index])[len(df_fichier.iloc[page][index]) - 12]
    if journal is not None:
        if journal.isnumeric() and len(journal) > 2:
            journal = (df_fichier.iloc[page][index])[8]
            contre_partie = (df_fichier.iloc[page][index])[9]
            if num_cheque is None:
                num_cheque = (df_fichier.iloc[page][index])[10]
    if test_colum_12 is not None and test_colum_12 != '':
        if not test_colum_12.isnumeric() or len(test_colum_12) == 2:
            journal = test_colum_12
            contre_partie = (df_fichier.iloc[page][index])[len(df_fichier.iloc[page][index]) - 11]
            num_cheque = (df_fichier.iloc[page][index])[len(df_fichier.iloc[page][index]) - 9]
    if journal is None:
        if (df_fichier.iloc[page][index])[7] is not None:
            journal = (df_fichier.iloc[page][index])[7]
            contre_partie = (df_fichier.iloc[page][index])[len(df_fichier.iloc[page][index]) - 12]
            num_cheque = (df_fichier.iloc[page][index])[len(df_fichier.iloc[page][index]) - 10]
        else:
            contre_partie = ''
            num_cheque = ''
    return journal, contre_partie, num_cheque
