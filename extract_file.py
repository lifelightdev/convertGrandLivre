import pdfplumber


def extract_file(my_file: str):

    pdf = pdfplumber.open(my_file)
    page = pdf.pages[0]
    return page.extract_table()
