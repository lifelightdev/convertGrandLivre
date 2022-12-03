from datetime import datetime
import pandas
from constante import SEPARATEUR_CSV, ENCODING, DOSSIER_ETAPE
from extract_file import extract_liste_de_compte


def etape_1_liste_compte(etape, file_name):
    debut = datetime.today()
    liste_compte = {}
    if etape == 'True':
        df_liste_compte = pandas.read_csv(f"{DOSSIER_ETAPE}/Etape_1_liste_des_comptes.csv", sep=SEPARATEUR_CSV,
                                          encoding=ENCODING)
    else:
        df_liste_compte = extract_liste_de_compte(file_name)

    nombre_de_ligne = len(df_liste_compte)
    index = 0
    while nombre_de_ligne > index:
        liste_compte[str(df_liste_compte.iloc[index, 0])] = df_liste_compte.iloc[index, 1]
        index = index + 1
    max_size_compte = max(df_liste_compte['Intitulé du compte'].str.len())
    fin = datetime.today()
    print(f"Fin de l'étape 1 (recherche des comptes et leurs libellé) en {fin - debut}")
    return liste_compte, max_size_compte