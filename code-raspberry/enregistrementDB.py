
import json
import parametres as param
import sqlite3
import paho.mqtt.client as mqtt
import datetime
import time

##############################################################################################################################
#### Ce fichier python permet de gérer la base de données. Il créé et purge les différentes tables de celle-ci.
#### Il permet également d'enregistrer toutes les données s'échangeant en MQTT dans la basse de données
#### Version 1.0 du 06/01/2024
##############################################################################################################################


################ dbFermeDesOurs.py ################
path = 'dbFermeDesOursV2.db'

def creationTable(nomTable, commandeSQL):
    try:
        connexion = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        curseur = connexion.cursor()
        print("Connecté à SQLite" + path)
        setUp_Table = commandeSQL
        curseur.execute(setUp_Table)
        connexion.commit()
        curseur.close()
    except sqlite3.Error as error:
        print("erreur de connection a la base ou la "+ nomTable, error)
    finally:
        if connexion:
            connexion.close()
            print(nomTable + " a été créée. Fermeture de la connection a la base de donnees")


def enregistrerTable(nomTable, commandeSQL, data_tuples):
    try:
        connexion = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        curseur = connexion.cursor()
        print("Connecté à SQLite" + path)
        curseur.execute(commandeSQL,data_tuples)
        connexion.commit()
        curseur.close()
    except sqlite3.Error as error:
        print("erreur de connection a la base ou a"+ nomTable , error)
    finally: 
        if connexion:
            connexion.close()
            print("Les valeurs ont été ajoutéés à "+nomTable+". Fermeture de la connection a la base de donnees")

def insertDummies():
    enregistrerTable("Grange","Anemometre",22.0,"'2024-01-07 20:28:04.320'")

    ################ MQTT ###############

def on_connect(client, userdata,flags, rc):
    if rc==0:
        print("Connected to MQTT Broker! Returned code: "+str(rc))
    else:
        print("Failed to connect. Returned code: "+str(rc))

def on_message(client, userdata, msg):
    topic=msg.topic
    message_decode=str(msg.payload.decode("utf-8","ignore"))
    if topic == param.topicGrangeAnemoDonnees:
        message_in=json.loads(message_decode)
        print("valeur relevée: "+str(message_in["valeuMoyenne"]) +" date de relevé : " + str(message_in["date"]))
        #TODO a changer
        enregistrerTable("tableReleveDonnees",'''INSERT INTO tableReleveDonnees(lieu, categorie, valeur,date) VALUES(?,?,?,?) ;''', (str(message_in["lieu"]),str(message_in["categorie"]),str(message_in["valeur"]) ,str(message_in["date"])))
    
def on_disconnect(client, userdata, rc):
    print("Client Got Disconnected")
    if rc != 0: 
        print("Unexpected MQTT disconnection. Will auto-reconnect")



################ Creation des tables ###############

################ Table LogSerres ###############

################ Table Releve Donnees ###############
print("\n\n")
creationTable("tableReleveDonnees",'''CREATE TABLE IF NOT EXISTS tableReleveDonnees( id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,lieu TEXT, categorie TEXT,valeur REAL, date TEXT);''')
enregistrerTable("tableReleveDonnees",'''INSERT INTO tableReleveDonnees(lieu, categorie, valeur,date) VALUES(?,?,?,?) ;''', ("Grange","Anemometre",28 ,"'2024-01-07 20:28:04.320'"))

################ Table LogSerres ###############
creationTable("tableLogSerres",'''CREATE TABLE IF NOT EXISTS tableLogSerres( id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, type TEXT, lieu TEXT, message TEXT, date TEXT);''')
enregistrerTable("tableLogSerres",'''INSERT INTO tableLogSerres(type, lieu, message, date) VALUES(?,?,?,?) ;''', ("informatif","grange","aled y a rien qui marche" ,"'2024-01-08 20:28:04.320'"))

################ Table EtatSerres ###############
creationTable("tableEtatSerres",'''CREATE TABLE IF NOT EXISTS tableEtatSerres( id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, lieu TEXT, appareil TEXT, mode TEXT, etat TEXT, date TEXT);''')
enregistrerTable("tableEtatSerres",'''INSERT INTO tableEtatSerres(lieu, appareil, mode, etat, date) VALUES(?,?,?,?,?) ;''', ("grange","ventilation","auto", "marche" ,"'2024-01-09 20:28:04.320'"))

################ Table ProfilsHisto ###############
creationTable("tableProfilsHisto",'''CREATE TABLE IF NOT EXISTS tableProfilsHisto( id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, lieu TEXT, profil TEXT, date TEXT);''')
enregistrerTable("tableProfilsHisto",'''INSERT INTO tableProfilsHisto(lieu, profil, date) VALUES(?,?,?) ;''', ("grange","profil3","'2024-01-09 20:28:04.320'"))
creationTable("tableProfilsHisto",'''CREATE TABLE IF NOT EXISTS tableProfilsHisto( id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, lieu TEXT, profil TEXT, date TEXT);''')
enregistrerTable("tableProfilsHisto",'''INSERT INTO tableProfilsHisto(lieu, profil, date) VALUES(?,?,?) ;''', ("grange","profil4","'2024-01-07 20:28:04.320'"))

################ Table ProfilsActifs ###############
creationTable("tableProfilsActifs",'''CREATE TABLE IF NOT EXISTS tableProfilsActifs( id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, lieu TEXT, profil TEXT, date TEXT);''')
enregistrerTable("tableProfilsActifs",'''INSERT INTO tableProfilsActifs(lieu, profil, date) VALUES(?,?,?) ;''', ("grange","profil3","'2024-01-09 20:28:04.320'"))

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(param.IP_ADRESS, param.PORT)
#TODO securiser la connection en cas de perte de connection/ mauvaise connection
mqtt_client.loop_start()
mqtt_client.subscribe(param.topicGrangeAnemoDonnees)
mqtt_client.subscribe(param.topicGrangeAnemoParamRep)


while(True):
        time.sleep(0.05)

