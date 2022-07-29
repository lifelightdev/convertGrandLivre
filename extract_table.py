def extract_entete(table, ligne):
    return table[ligne]

def extract_total(ligne):
    if ligne[0].startswith('TOTAL DU COMPTE : ', 0, 18):
        return ligne[0]
    return None

def extact_total_montant(ligne):
    compte = ligne[18:].split()[0]
    montants = ligne[18:].split()
    montants.remove(compte)
    retour = [compte]
    montant = ''
    for nombre in range(0, len(montants)):
        if montants[nombre].find(',') > 0:
            retour.append(montant + montants[nombre])
            montant = ''
        else:
            montant = montant + montants[nombre]
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
            montant = montant + montants[nombre]
    return retour
