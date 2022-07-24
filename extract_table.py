def extract_entete(table, ligne):
    return table[ligne]

def extract_compte(ligne, param):
    if ligne[0].startswith('Compte', 0, 6):
        return ligne[0]
    return None
