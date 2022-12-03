import pdfplumber
import pandas
from constante import PATTERN_PIECE, DOSSIER_ETAPE, SEPARATEUR_CSV, ENCODING, DECIMAL

table_settings = {
    "horizontal_strategy": "lines"
}


def extract_file(my_file: str):
    les_pages = []
    with pdfplumber.open(my_file) as pdf:
        for i in range(0, len(pdf.pages)):
            page = pdf.pages[i].extract_tables(table_settings)
            les_pages = les_pages + page
    print(f"Il y a {len(pdf.pages)} pages dans le fichier PDF.")
    return les_pages


def extract_page_in_file(my_file: str, num_page: int):
    with pdfplumber.open(my_file) as pdf:
        page = pdf.pages[num_page].extract_tables(table_settings)
    return page


def extract_nombre_de_page(my_file: str):
    with pdfplumber.open(my_file) as pdf:
        nombre = len(pdf.pages)
    return nombre

def extract_liste_de_compte(my_file: str):
    libelle = ''
    trouve_compte = False
    fin_libelle = True
    df_liste_compte = pandas.DataFrame(columns=["Compte", "Intitulé du compte"])
    nombre_de_compte = 0
    with pdfplumber.open(my_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text().split()
            for index, valeur in enumerate(text):
                if not trouve_compte and valeur == 'Compte':
                    compte = text[index + 2]
                    trouve_compte = True
                    fin_libelle = False
                else:
                    if trouve_compte and not fin_libelle:
                        if valeur != ':':
                            if valeur != compte:
                                if text[index - 2] == 'Copropriétaire':
                                    compte = f"450{int(valeur)}"
                                else:
                                    if PATTERN_PIECE.match(valeur) is None:
                                        if valeur == 'Edité':
                                            trouve_compte = False
                                            fin_libelle = True
                                            nombre_de_compte = nombre_de_compte + 1
                                            df_liste_compte.loc[nombre_de_compte] = [compte, libelle]
                                            libelle = ''
                                        else:
                                            libelle = libelle + ' ' + valeur
                                            libelle = libelle.lstrip()
                                    else:
                                        trouve_compte = False
                                        fin_libelle = True
                                        nombre_de_compte = nombre_de_compte + 1
                                        df_liste_compte.loc[nombre_de_compte] = [compte, libelle]
                                        libelle = ''

    # Ecriture du dataframe de sortie
    df_liste_compte.to_csv(f"{DOSSIER_ETAPE}/Etape_1_liste_des_comptes.csv", sep=SEPARATEUR_CSV, encoding=ENCODING,
                           decimal=DECIMAL, index=False)
    return df_liste_compte
