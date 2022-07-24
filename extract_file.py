import pdfplumber


def extract_file(my_file: str):
    les_pages = []
    with pdfplumber.open(my_file) as pdf:
        for i in range(0, len(pdf.pages)):
            page = pdf.pages[i].extract_table()
            les_pages = les_pages + page
    return page

def extract_page_in_file(my_file: str, num_page: int):
    with pdfplumber.open(my_file) as pdf:
        page = pdf.pages[num_page].extract_table()
    return page

def extract_nombre_de_page(my_file: str):
    with pdfplumber.open(my_file) as pdf:
        nombre = len(pdf.pages)
    return nombre
