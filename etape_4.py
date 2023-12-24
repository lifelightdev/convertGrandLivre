#########
# Vérification des totaux du grand livre
#########

from datetime import datetime


def etape_4_total(df_sortie):
    debut = datetime.today()
    df_sortie = verif_total(df_sortie)
    fin = datetime.today()
    print(f"Fin de l'étape 4 (vérification des totaux) en {fin - debut}")
    return df_sortie


def verif_total(df_sortie):
    total_debit = 0
    total_credit = 0
    total_complet_debit = 0
    total_complet_credit = 0
    for index in df_sortie.index:
        if df_sortie["Libellé"][index] is not None:
            if (df_sortie["Libellé"][index].startswith('Total compte')
                    or df_sortie["Libellé"][index].startswith('TOTAL DU COMPTE')):
                total_complet_credit, total_complet_debit, total_credit, total_debit = verif_totaux_compte(
                    df_sortie, index, total_complet_credit, total_complet_debit, total_credit, total_debit)
                if total_debit > total_credit:
                    if df_sortie["Solde Débit"][index] == float(round(round(total_debit, 2) - round(total_credit, 2), 2)):
                        message = "OK"
                    else:
                        message = (f"(Le total débit = {round(total_debit, 2)} "
                                   f"et le total crédit = {round(total_credit, 2)}) "
                                   f"Solde des débits ({round(total_debit, 2) - round(total_credit, 2)}) "
                                   f"n'est pas égale au solde du grand livre = ({df_sortie['Solde Débit'][index]})")
                else:
                    if df_sortie["Solde Crédit"][index] != float(round(total_credit - total_debit, 2)):
                        message = (f"(le total du débit = {round(total_debit, 2)} "
                                   f"et le total du crédit = {round(total_credit, 2)}) "
                                   f"Solde des crédits {round(round(total_credit, 2) - round(total_debit, 2), 2)}) "
                                   f"n'est pas égale au solde du grand livre = ({df_sortie['Solde Crédit'][index]})")
                    else:
                        message = "OK"
                if len(message) > 0:
                    df_sortie['Vérification Solde'][index] = message
                else:
                    df_sortie['Vérification Solde'][
                        index] = "OK"
                total_debit = 0
                total_credit = 0
            elif (df_sortie["Libellé"][index] == 'Total Général du Grand-Livre'
                  or df_sortie["Libellé"][index] == 'Total immeuble'):
                message = ''
                total_complet_credit, total_complet_debit = verif_totaux_grand_livre(df_sortie, index,
                                                                                     total_complet_credit,
                                                                                     total_complet_debit)
                if total_complet_debit > total_complet_credit:
                    if df_sortie["Solde Débit"][index] == (total_complet_debit - total_complet_credit):
                        message = (f"OK le total des débits = {total_complet_debit} "
                                   f"le total des crédits = {total_complet_credit}")
                    else:
                        message = f"Solde général des débits ({float(total_complet_debit - total_complet_credit)}) " \
                                  f"n'est pas égale au solde du grand livre = ({df_sortie['Solde Débit'][index]})"
                if total_complet_credit > total_complet_debit:
                    if df_sortie["Solde Crédit"][index] != (total_complet_credit - total_complet_debit):
                        message = f"Solde général des crédits ({float(total_complet_credit - total_complet_debit)}) " \
                                  f"n'est pas égale au solde du grand livre = ({df_sortie['Solde Crédit'][index]})"
                if len(message) > 0:
                    df_sortie['Vérification Solde'][index] = message
                else:
                    df_sortie['Vérification Solde'][
                        index] = (f"OK le total des débits = {total_complet_debit} "
                                  f"le total des crédits = {total_complet_credit}")
            else:
                total_debit = total_debit + df_sortie['Débit'][index]
                total_credit = total_credit + df_sortie['Crédit'][index]
    return df_sortie


def remove_compte_in_total(df_sortie, ids_ligne_totaux):
    for index in ids_ligne_totaux:
        df_sortie["Compte"][index] = ""
    return df_sortie


def verif_totaux_grand_livre(df_sortie, index, total_complet_credit, total_complet_debit):
    message = ''
    total_complet_debit = round(total_complet_debit, 2)
    total_complet_credit = round(total_complet_credit, 2)
    if float(total_complet_debit) != df_sortie["Débit"][index]:
        message = f"Le total des débits ({float(total_complet_debit)}) n'est pas égale au total du grand livre" \
                  f" ({df_sortie['Débit'][index]}) \n"
    if float(total_complet_credit) != df_sortie["Crédit"][index]:
        message = f"Le total des crédits ({total_complet_credit}) n'est pas égale au total du grand livre " \
                  f"({df_sortie['Crédit'][index]}) \n"
    if len(message) > 0:
        df_sortie['Vérification Débit/Crédit'][index] = message
    else:
        df_sortie['Vérification Débit/Crédit'][index] = 'OK'
    return total_complet_credit, total_complet_debit


def verif_totaux_compte(df_sortie, index, total_complet_credit, total_complet_debit, total_credit, total_debit):
    message = ''
    total_debit = round(float(total_debit), 2)
    total_credit = round(float(total_credit), 2)
    if float(total_debit) != df_sortie["Débit"][index]:
        message = f"Le total des débits ({float(total_debit)}) n'est pas égale au total du grand livre = " \
                  f"({df_sortie['Débit'][index]}) \n"
    if float(total_credit) != df_sortie["Crédit"][index]:
        message = f"Le total des crédits ({total_credit}) n'est pas égale au total du grand livre " \
                  f"({df_sortie['Crédit'][index]}) \n"
    if len(message) > 0:
        df_sortie['Vérification Débit/Crédit'][index] = message
    else:
        df_sortie['Vérification Débit/Crédit'][index] = "OK"
    total_complet_debit = total_complet_debit + total_debit
    total_complet_credit = total_complet_credit + total_credit
    return total_complet_credit, total_complet_debit, total_credit, total_debit
