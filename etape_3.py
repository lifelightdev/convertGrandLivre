from datetime import datetime
from constante import DOSSIER_ETAPE, SEPARATEUR_CSV, ENCODING, DECIMAL


def etape_3_add_count(df_sortie):
    debut = datetime.today()
    compte = ''
    libelle = ''
    nombre_de_ligne_sortie = len(df_sortie) - 1
    while nombre_de_ligne_sortie > 0:
        if df_sortie["Libellé"][nombre_de_ligne_sortie] == "TOTAL DU COMPTE":
            compte = df_sortie["Compte"][nombre_de_ligne_sortie]
            libelle = df_sortie["Intitulé du compte"][nombre_de_ligne_sortie]
        else:
            df_sortie["Compte"][nombre_de_ligne_sortie] = compte
            df_sortie["Intitulé du compte"][nombre_de_ligne_sortie] = libelle
        nombre_de_ligne_sortie = nombre_de_ligne_sortie - 1
    # Ecriture du dataframe de sortie
    df_sortie.to_csv(f"{DOSSIER_ETAPE}/Etape_3_Grand_livre_avec_compte.csv", sep=SEPARATEUR_CSV, encoding=ENCODING,
                     decimal=DECIMAL, index=False)

    fin = datetime.today()
    print(f"Fin de l'étape 3 (écriture des comptes) en {fin - debut}")

    return df_sortie
