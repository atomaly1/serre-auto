from pathlib import Path
import sys
import pandas as pd
import datetime

##############################################################################################################################
#### Ce fichier python contient les différents paramètres globaux du système
#### Version 1.0 du 06/01/2024
##############################################################################################################################


################ MQTT ###############
IP_ADRESS ="172.20.10.2" #ip du téléphone Alban
PORT=1883


################ Topics ###############
#GRANGE==================
#Parametres
topicGrangeAnemoParamReq= 'FermeDesOurs/Grange/Capteurs/Anemometre/Parametres/Requete'
topicGrangeAnemoParamRep= 'FermeDesOurs/Grange/Capteurs/Anemometre/Parametres/Reponse'
#Donnees
topicGrangeAnemoDonnees= 'FermeDesOurs/Grange/Capteurs/Anemometre/Donnees'

#Serre 1==================




################ Fonctions ###############

def getlatestvalue(donnees:pd.DataFrame,serreSelectionne,capteurSelectionne)->pd.DataFrame:
    data_filtre = donnees.copy()
    data_filtre = filtrageDonnes(data_filtre,serreSelectionne,capteurSelectionne,None,None)
    return data_filtre.tail(1)
    


def filtrageDonnes(donnees:pd.DataFrame,serreSelectionne,capteurSelectionne,dateDebut,dateFin):
    # print("serre: "+str(serreSelectionne)+ " type: "+str(type(serreSelectionne)))
    # print("capteur: "+str(capteurSelectionne)+ " type: "+str(type(capteurSelectionne)))
    # print("dateDebut: "+str(dateDebut)+ " type: "+str(type(dateDebut)))
    # print("dateFin: "+str(dateFin)+ " type: "+str(type(dateFin)))
    # print(donnees)
    data_filtre_affichage = donnees.copy()
    if capteurSelectionne != None:
        # print("if 1")
        data_filtre_affichage = data_filtre_affichage[data_filtre_affichage['categorie'].isin(capteurSelectionne)].copy()
    if serreSelectionne != None:
        # print("if 2")
        data_filtre_affichage = data_filtre_affichage[data_filtre_affichage['lieu'].isin(serreSelectionne)].copy()
    if dateDebut != None and dateFin != None:
        # print("if 3")
        data_filtre_affichage = data_filtre_affichage[(pd.to_datetime(data_filtre_affichage['date']) >= dateDebut) & (pd.to_datetime(data_filtre_affichage['date']) <= dateFin)].copy()
    if dateDebut != None and dateFin == None:
        # print("if 4")
        data_filtre_affichage = data_filtre_affichage[pd.to_datetime(data_filtre_affichage['date']) >= pd.to_datetime(dateDebut)].copy()
    if dateDebut == None and dateFin != None:
        # print("if 5")
        data_filtre_affichage = donnees[pd.to_datetime(donnees['date']) <= dateFin].copy()  

    # print(data_filtre_affichage)
    return data_filtre_affichage

def test():
    data = pd.read_sql('SELECT * FROM tab_sensor_data_test', 'sqlite:///db_sensors.db')
    data_filtre_affichage = filtrageDonnes(data,["serre_1"],["temperature","humidite"],"2023-10-23 18:55:04.320","2023-10-23 23:55:04.320")
