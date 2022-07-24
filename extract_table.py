def extract_entete(table, ligne):
    return table[ligne]

def extract_compte(ligne):
    if ligne[0].startswith('Compte', 0, 6):
        list_of_word = ligne[0].split()
        compte = list_of_word[2]
        nom = ' '.join(list_of_word[3:])
        return [compte, nom]
    return None

def extract_total(ligne):
    if ligne[0].startswith('TOTAL DU COMPTE : ', 0, 18):
        return ligne[0]
    return None
