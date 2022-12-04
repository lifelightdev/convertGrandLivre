import re

PATTERN_PIECE = re.compile("[0-9]{6}/[0-9]{2}/[0-9]{2}")
SEPARATEUR_CSV = ';'
ENCODING = 'ANSI'
DECIMAL = ','
DOSSIER_ETAPE = 'Etape'
DOSSIER_SORTIE = 'Sortie'

COLUMNS_NAME = ["Compte", "Intitulé du compte", "Pièce", "Date", "Journal", "Libellé", "N° facture", "Contre partie",
                "N° chèque", "Débit", "Crédit", "Solde Débit", "Solde Crédit", "Vérification Débit/Crédit",
                "Vérification Solde"]

COLUMNS_NAME_COMPTE = ["Compte", "Intitulé du compte", "Pièce", "Date", "Journal", "Libellé", "N° facture",
                       "Contre partie", "N° chèque","Débit", "Crédit", "Solde"]