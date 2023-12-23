def extract_entete(table, ligne):
    return table[ligne]

def extract_total(ligne):
    if ligne[0].startswith('TOTAL DU COMPTE : ', 0, 18):
        return ligne[0]
    if ligne[0].startswith('Total compte ', 0, 18):
        return ligne[0]
    return None

def extact_total_montant(ligne):
    retour = []
    montant = ''
    for nombre in range(0, len(ligne)):
        if (ligne[nombre] != None):
            if ligne[nombre].find(',') > 0:
                retour.append(f"{montant}{ligne[nombre]}")
                montant = ''
            else:
                if ligne[nombre].isnumeric():
                    montant = f"{montant}{ligne[nombre]}"
    return retour

def extact_total_grand_livre(ligne):
    montants = ligne[28:].split()
    retour = []
    montant = ''
    for nombre in range(0, len(montants)):
        if montants[nombre].find(',') > 0:
            retour.append(montant + montants[nombre])
            montant = ''
        else:
            if montants[nombre].isnumeric():
                montant = montant + montants[nombre]
    return retour
