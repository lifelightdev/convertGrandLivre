from datetime import datetime
import pandas
from constante import COLUMNS_NAME_LIST_COMPTE, COPRO_S, COPRO_N
from outil import is_ligne_libelle_compte


def etape_1_liste_compte(pages, copro):
    debut = datetime.today()
    liste_compte = {}
    df_liste_compte = extract_liste_de_compte(pages, copro)
    nombre_de_ligne = len(df_liste_compte)
    index = 0
    while nombre_de_ligne > index:
        liste_compte[str(df_liste_compte.iloc[index, 0])] = df_liste_compte.iloc[index, 1]
        index = index + 1
    fin = datetime.today()
    print(f"Fin de l'étape 1 (recherche des comptes et leurs libellé) en {fin - debut}")
    return liste_compte


def extract_liste_de_compte(pages, copro: str):
    df_liste_compte = pandas.DataFrame(columns=COLUMNS_NAME_LIST_COMPTE)
    nombre_de_compte = 0
    for page in pages:
        for ligne in page:
            if copro == COPRO_S:
                df_liste_compte = compte_s(df_liste_compte, ligne)
            if copro == COPRO_N:
                nombre_de_compte, df_liste_compte = compte_n(df_liste_compte, nombre_de_compte, ligne)
    return df_liste_compte


def compte_n(df_liste_compte, nombre_de_compte, text):
    libelle = ''
    if len(text) == 10:
        if is_ligne_libelle_compte(text):
            compte = text[2]
            libelle = text[5]
            df_liste_compte.loc[nombre_de_compte] = [compte, libelle]
            nombre_de_compte = nombre_de_compte + 1
    if len(text) == 9:
        if text[0] == '' and text[1] == None \
                and not not text[2] and text[3] == '' \
                and not not text[4] and text[5] == None \
                and text[6] == "" and text[7] == None \
                and text[8] == None:
            compte = text[2]
            libelle = text[4]
            df_liste_compte.loc[nombre_de_compte] = [compte, libelle]
            nombre_de_compte = nombre_de_compte + 1
    if len(text) == 22:
        compte = text[4]
        if not (text[8] == None):
            if not (text[7] == None):
                libelle = text[7]
            libelle = libelle + text[8]
        if (not compte == None) and (not libelle == None) and (not libelle == ''):
            df_liste_compte.loc[nombre_de_compte] = [compte, libelle]
            nombre_de_compte = nombre_de_compte + 1
    if len(text) == 20 or len(text) == 21:
        compte = text[4]
        if not (text[7] == None):
            if not (text[5] == None):
                libelle = text[5]
            if not (text[6] == None):
                libelle = libelle + text[6]
            libelle = libelle + text[7]
        else:
            if not (text[5] == None):
                libelle = text[5]
            if not (text[8] == None):
                libelle = libelle + text[8]
        if (not compte == None) and (not libelle == None) and (not libelle == ''):
            df_liste_compte.loc[nombre_de_compte] = [compte, libelle]
            nombre_de_compte = nombre_de_compte + 1
    return nombre_de_compte, df_liste_compte


def compte_s(df_liste_compte, ligne):
    for colonne in ligne:
        if not colonne == None:
            if colonne.startswith('Compte : '):
                colonne = colonne.replace('Compte : ', '')
                if colonne.startswith('450 Copropriétaire : '):
                    colonne = colonne.replace('450 Copropriétaire : ', '')
                    compte = '450' + colonne.split()[0]
                    libelle = colonne.replace(colonne.split()[0], '').lstrip()
                else:
                    compte = colonne.split()[0]
                    libelle = colonne.replace(compte, '').lstrip()
                df_liste_compte.loc[df_liste_compte.size] = [compte, libelle]
    return df_liste_compte
