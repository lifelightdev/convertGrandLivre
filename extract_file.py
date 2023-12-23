import pdfplumber
from constante import COPRO_N, COPRO_S

table_settings_ligne = {"vertical_strategy": "lines",
                        "horizontal_strategy": "text",
                        "min_words_vertical": 2,
                        "explicit_vertical_lines": [],
                        "explicit_horizontal_lines": []}

table_settings_colonne = {"vertical_strategy": "lines",
                          "horizontal_strategy": "lines",
                          "explicit_vertical_lines": [],
                          "explicit_horizontal_lines": [],
                          "intersection_tolerance": 2
                          }


def extract_file(my_file: str, copro: str):
    les_pages = []
    with pdfplumber.open(my_file) as pdf:
        page = pdf.pages[0].extract_text().split()
        arrete_au, date_impression, nom_syndic = extract_donnees(copro, page)
        nombre_de_page = len(pdf.pages)
        print(f"Il y a {nombre_de_page} pages dans le fichier PDF du syndic {nom_syndic} en date du {date_impression} "
              f"pour un arret des comptes au {arrete_au}.")
        for index in range(0, len(pdf.pages)):
            page = pdf.pages[index].extract_tables(table_settings_ligne)
            les_pages = les_pages + page
    return les_pages, nom_syndic, date_impression, arrete_au


def extract_donnees(copro, page):
    if copro == COPRO_N:
        nom_syndic = f"{page[0]} {page[1]} {page[2]}"
        date_impression = page[3]
        arrete_au = page[16]
        arrete_au = arrete_au.replace('/', ' ')
        arrete_au = arrete_au.split()
        arrete_au = f"{arrete_au[2]}-{arrete_au[1]}-{arrete_au[0]}"
    if copro == COPRO_S:
        nom_syndic = page[0]
        date_impression = page[len(page) - 6]
        arrete_au = page[17]
    arrete_au = arrete_au.replace('/', '-')
    date_impression = date_impression.replace('/', ' ')
    date_impression = date_impression.split()
    date_impression = f"{date_impression[2]}-{date_impression[1]}-{date_impression[0]}"
    return arrete_au, date_impression, nom_syndic
