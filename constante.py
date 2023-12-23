import re

PATTERN_PIECE = re.compile("[0-9]{6}/[0-9]{2}/[0-9]{2}")
SEPARATEUR_CSV = ';'
ENCODING = 'ANSI'
DECIMAL = ','
DOSSIER_SORTIE = 'Sortie'

COLUMNS_NAME_S = ["Compte", "Intitulé du compte", "Pièce", "Date", "Journal", "Libellé", "N° facture", "Débit",
                  "Crédit", "Solde Débit", "Solde Crédit", "Vérification Débit/Crédit", "Vérification Solde"]

COLUMNS_NAME_N = ["Compte", "Intitulé du compte", "Pièce", "Date", "Journal", "Libellé", "Contre partie", "N° chèque",
                  "Débit", "Crédit", "Solde Débit", "Solde Crédit", "Vérification Débit/Crédit", "Vérification Solde"]


COLUMNS_NAME_COMPTE_S = ["Compte", "Intitulé du compte", "Pièce", "Date", "Journal", "Libellé", "N° facture", "Débit",
                         "Crédit", "Solde"]

COLUMNS_NAME_COMPTE_N = ["Compte", "Intitulé du compte", "Pièce", "Date", "Journal", "Libellé", "Contre partie",
                         "N° chèque", "Débit", "Crédit", "Solde"]

COLUMNS_NAME_LIST_COMPTE = ["Compte", "Intitulé"]

COPRO_N = "N"
COPRO_S = "S"

PATTERN_DATE = re.compile("^\\d{2}/\\d{2}/\\d{4}$")
