
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


################ Creation des tables ###############

################ Table Releve Donnees ###############

path = 'dbFermeDesOurs.db'

def creationTableReleveDonnes():
    try:
        connexion = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        curseur = connexion.cursor()
        print("Connecté à SQLite")
        setUp_Table ='''CREATE TABLE IF NOT EXISTS tableReleveDonnees( id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, topic TEXT, lieu TEXT, categorie TEXT,valeur REAL, date TEXT);'''
        curseur.execute(setUp_Table)
        connexion.commit()
        curseur.close()
    except sqlite3.Error as error:
        print("Error while connecting to sqlite", error)
    finally:
        if connexion:
            connexion.close()
            print("The SQLite connection is closed")

def enregistrerReleveDonnes(topic, lieu, categorie, valeur,date):
    try:
        connexion = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        curseur = connexion.cursor()
        print("Connected to SQLite")
        insert_data = '''INSERT INTO tableReleveDonnees(topic, lieu, categorie, valeur,date) VALUES(?,?,?,?,?) ;'''
        data_tuples = (topic,lieu,categorie, valeur,date)
        curseur.execute(insert_data,data_tuples)
        connexion.commit()
        curseur.close()
    except sqlite3.Error as error:
        print("Error while connecting to sqlite", error)
    finally:
        if connexion:
            connexion.close()
            print("The SQLite connection is closed")

################ Table Consignes ###############

path = 'dbFermeDesOurs.db'

def creationTableConsignes():
    try:
        connexion = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        curseur = connexion.cursor()
        print("Connecté à SQLite")
        setUp_Table ='''CREATE TABLE IF NOT EXISTS tableReleveDonnees( id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, topic TEXT, lieu TEXT, categorie TEXT,valeur REAL, date TEXT);'''
        curseur.execute(setUp_Table)
        connexion.commit()
        curseur.close()
    except sqlite3.Error as error:
        print("Error while connecting to sqlite", error)
    finally:
        if connexion:
            connexion.close()
            print("The SQLite connection is closed")

def enregistrerConsignes(topic, lieu, categorie, valeur,date):
    try:
        connexion = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        curseur = connexion.cursor()
        print("Connected to SQLite")
        insert_data = '''INSERT INTO tableReleveDonnees(topic, lieu, categorie, valeur,date) VALUES(?,?,?,?,?) ;'''
        data_tuples = (topic,lieu,categorie, valeur,date)
        curseur.execute(insert_data,data_tuples)
        connexion.commit()
        curseur.close()
    except sqlite3.Error as error:
        print("Error while connecting to sqlite", error)
    finally:
        if connexion:
            connexion.close()
            print("The SQLite connection is closed")            

def insertDummies():
    enregistrerReleveDonnes("FermeDesOurs/Grange/Capteurs/Anemometre/Donnees","Grange","Anemometre",22.0,"'2024-01-07 20:28:04.320'")

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
        enregistrerReleveDonnes("FermeDesOurs/Grange/Capteurs/Anemometre/Donnees","Grange","Anemometre",str(message_in["valeuMoyenne"]) ,str(message_in["date"]))
        #récupérer les 3 premiers chants soit dans le topic soit changer le json
    
    
def on_disconnect(client, userdata, rc):
    print("Client Got Disconnected")
    if rc != 0: 
        print("Unexpected MQTT disconnection. Will auto-reconnect")

creationTableReleveDonnes()

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(param.IP_ADRESS, param.PORT)
mqtt_client.loop_start()
mqtt_client.subscribe(param.topicGrangeAnemoDonnees)
mqtt_client.subscribe(param.topicGrangeAnemoParamRep)

print("va dans le while")
while(True):
        time.sleep(0.05)

