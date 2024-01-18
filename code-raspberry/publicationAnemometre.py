from gpiozero import MCP3008
import paho.mqtt.client as mqtt
import datetime
import json
from time import sleep
import parametres as param
import random

##############################################################################################################################
#### Ce fichier python permet de publier les valeurs de l'anemomètre placé sur la serre
#### Version 1.0 du 07/01/2024
##############################################################################################################################



#==========SETUP ADC==========#
# creation d'un objet channel 0 de l'objet ADC MCP3008 
# un channel est une entrée analogique, le MCP3008 peut en avoir jusqu'à 8

channel_anemometre = MCP3008(0) # a activer en version finale

#==========SETUP VALUES==========#

valeurAleatoire = 20.0 # pour les tests
maxVent = 0
temporisationEnvoi = 5 #temps entre deux publications de vent
temporisationReleves = 20

#==========SETUP MQTT==========#

def on_connect(client, userdata,flags, rc):
    if rc==0:
        print("Connected to MQTT Broker! Returned code: "+str(rc))
    else:
        print("Failed to connect. Returned code: "+str(rc))

def on_message(client, userdata, msg):
    topic=msg.topic
    message_decode=str(msg.payload.decode("utf-8","ignore"))
    #si c'est une nouvelle valeur setup alors on l'enregistre en local
    if topic == param.topicGrangeAnemoParamRep:
        message_in=json.loads(message_decode)
        maxVent = message_in["valeurMax"]
        print("nouvelle valeur max : " + str(maxVent))
    #sinon on ne fait rien
    
def on_disconnect(client, userdata, rc):
    print("Client Got Disconnected")
    if rc != 0: 
        print("Unexpected MQTT disconnection. Will auto-reconnect")
    
def  recupererValeursSetup():
    pass

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(param.IP_ADRESS, param.PORT)
mqtt_client.loop_start()
mqtt_client.subscribe(param.topicGrangeAnemoDonnees)
mqtt_client.subscribe(param.topicGrangeAnemoParamRep)

#==========RELEVE DU VENT==========#

def releveVent(temporisationReleves) -> float:
    nbValeurs = 3
    sommeValeurs = 0.0
    # ajouter un try catch
    for valeur in nbValeurs:
        valeur = 6*channel_anemometre.value # relevé
        sommeValeurs = sommeValeurs + valeur
        sleep(temporisationReleves)
    valeurMoyenne = sommeValeurs/nbValeurs
    return valeurMoyenne
    
#==========MAIN==========#

# envoie d'un get value
# récupération de la valeur (qui est udate si nouveau message durant le fonctionnement)
mqtt_client.publish(param.topicGrangeAnemoParamReq, "SETUP")

while True:

    valeurVent = releveVent(temporisationReleves) #valable pour l'anemometre final
    
    # valeurVent= random.randrange (valeurAleatoire-3,valeurAleatoire+3,1)
    # if valeurVent <0:
    #     valeurVent = 0
    # elif valeurVent>100:
    #     valeurVent = 100
    
    #valeurAleatoire= valeurVent
    dictionnaireMessage = {"lieu":"grange","categorie":"anemometre","valeur": valeurVent ,"date":str(datetime.datetime.now())}
    #exemple de reglage :     dictionnaireParametres = {"groupe":"grange","capteur": "anemometre","valeurMin": 0.0 , "valeurMax": 20.0 ,"date":str(datetime.datetime.now())}

    jsonMessage = json.dumps(dictionnaireMessage)

    mqtt_client.publish(param.topicGrangeAnemoDonnees,jsonMessage)
    sleep(temporisationEnvoi)



