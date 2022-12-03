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
