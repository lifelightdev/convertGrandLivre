import pdfplumber
import re
import pandas

table_settings = {
    "horizontal_strategy": "text"
}

PATTERN_PIECE = re.compile("[0-9]{6}/[0-9]{2}/[0-9]{2}")

def extract_file(my_file: str):
    les_pages = []
    with pdfplumber.open(my_file) as pdf:
        for i in range(0, len(pdf.pages)):
            page = pdf.pages[i].extract_tables(table_settings)
            les_pages = les_pages + page
    print(f"Il y a {len(pdf.pages)} pages.")
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
    retour = {}
    libelle = ''
    trouve_compte = False
    fin_libelle = True
    dataFame_liste_compte = pandas.DataFrame(columns=["Compte", "Intitulé du compte"])
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
                                    compte = valeur
                                else:
                                    if PATTERN_PIECE.match(valeur) is None:
                                        if valeur == 'Edité':
                                            trouve_compte = False
                                            fin_libelle = True
                                            retour[compte] = libelle
                                            nombre_de_compte = nombre_de_compte + 1
                                            dataFame_liste_compte.loc[nombre_de_compte] = [compte, libelle]
                                            libelle = ''
                                        else:
                                            libelle = libelle + ' ' + valeur
                                    else:
                                        trouve_compte = False
                                        fin_libelle = True
                                        retour[compte] = libelle
                                        nombre_de_compte = nombre_de_compte + 1
                                        dataFame_liste_compte.loc[nombre_de_compte] = [compte, libelle]
                                        libelle = ''
    # Ecriture du dataframe de sortie
    dataFame_liste_compte.to_csv(f"Etape_1_liste_des_comptes.csv", sep=';', encoding='ANSI', decimal=",", index=False)
    return retour
