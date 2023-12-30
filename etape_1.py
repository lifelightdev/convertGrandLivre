#########
# Extraction de la liste des comptes
#########

from datetime import datetime
import pandas
from constante import COLUMNS_NAME_LIST_COMPTE, COPRO_S, COPRO_N
from outil import is_ligne_null


def etape_1_liste_compte(pages, copro):
    debut = datetime.today()
    liste_compte = {}
    liste_compte_copro = []
    df_liste_compte = extract_liste_de_compte(pages, copro)
    nombre_de_ligne = len(df_liste_compte)
    index = 0
    while nombre_de_ligne > index:
        liste_compte[str(df_liste_compte.iloc[index, 0])] = df_liste_compte.iloc[index, 1]
        if df_liste_compte.iloc[index]['Compte'].startswith('450'):
            liste_compte_copro.append(df_liste_compte.iloc[index, 0])
        index = index + 1
    fin = datetime.today()
    print(f"Fin de l'étape 1 (recherche des comptes et leurs libellé) en {fin - debut}")
    return liste_compte, liste_compte_copro


def extract_liste_de_compte(pages, copro: str):
    df_liste_compte = pandas.DataFrame(columns=COLUMNS_NAME_LIST_COMPTE)
    for page in pages:
        for ligne in page:
            if copro == COPRO_S:
                df_liste_compte = compte_s(df_liste_compte, ligne)
            if copro == COPRO_N:
                df_liste_compte = compte_n(df_liste_compte, ligne)
    return df_liste_compte


def compte_n(df_liste_compte, text):
    libelle = ''
    if not is_ligne_null(text):
        if text[0] == '':
            if len(text) == 27 or len(text) == 29 or len(text) == 30 or len(text) == 31:
                compte = text[6]
                if compte is not None and compte != '':
                    if text[8] is not None:
                        libelle = libelle + text[8]
                    if text[9] is not None:
                        libelle = libelle + text[9]
                    if text[10] is not None:
                        libelle = libelle + text[10]
                    if text[11] is not None:
                        libelle = libelle + text[11]
                    if text[12] is not None:
                        libelle = libelle + text[12]
                    if libelle is not None and libelle != '':
                        libelle = libelle.replace('*************************************', '')
                        libelle = libelle.replace('************************************', '')
                        libelle = libelle.replace('***********************************', '')
                        libelle = libelle.replace('*********************************', '')
                        libelle = libelle.replace('****************', '')
                        libelle = libelle.replace('*****', ' ')
                        df_liste_compte.loc[df_liste_compte.size] = [compte, libelle]
    return df_liste_compte


def compte_s(df_liste_compte, ligne):
    for colonne in ligne:
        if colonne is not None:
            if colonne.startswith('Compte : '):
                colonne = colonne.replace('Compte : ', '')
                if colonne.startswith('450 Copropriétaire : '):
                    colonne = colonne.replace('450 Copropriétaire : ', '')
                    compte = '450' + str(int(str(colonne.split()[0])))
                    libelle = colonne.replace(colonne.split()[0], '').lstrip()
                else:
                    compte = colonne.split()[0]
                    libelle = colonne.replace(compte, '').lstrip()
                df_liste_compte.loc[df_liste_compte.size] = [compte, libelle]
    return df_liste_compte
