import argparse
from datetime import datetime
import pandas
from constante import COPRO_N, COPRO_S
from etape_1 import etape_1_liste_compte
from etape_2 import etape_2_create_df
from etape_3 import etape_3_file_compte_s
from etape_4 import etape_4_total
from etape_5 import etape_5_write_file_grand_livre
from etape_6 import etape_6_journaux
from etape_7 import etape_7_tresorerie
from extract_file import extract_file

pandas.options.mode.chained_assignment = None

def main():
    debut = datetime.today()
    print(f"Début à {debut}")
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--file", action="store", required=True,
                        help="Saisir le nom du fichier du grand livre")
    parser.add_argument("--copro", action="store", required=True,
                        help=f"Saisir le nom de la copropriété : {COPRO_S} ou {COPRO_N}")
    args = parser.parse_args()
    file_name = args.file
    pages, nom_syndic, date_impression, arrete_au = extract_file(file_name, args.copro)
    liste_cpt = etape_1_liste_compte(pages, args.copro)
    df_sortie = etape_2_create_df(pages, liste_cpt, args.copro)
    if args.copro == COPRO_S:
        etape_3_file_compte_s(df_sortie, nom_syndic, date_impression)
    df_sortie = etape_4_total(df_sortie, date_impression, nom_syndic, arrete_au)
    etape_5_write_file_grand_livre(df_sortie, date_impression, nom_syndic, arrete_au, args.copro)
    etape_6_journaux(df_sortie, nom_syndic, date_impression, arrete_au, args.copro)
    if args.copro == COPRO_N:
        etape_7_tresorerie(df_sortie, nom_syndic, date_impression, arrete_au)

    fin = datetime.today()
    print(f"Fin à {fin} pour une durée de {fin - debut}")


if __name__ == '__main__':
    main()
