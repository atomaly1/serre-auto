from gpiozero import MCP3008
import paho.mqtt.client as mqtt
import datetime
import json
from time import sleep

#==========SETUP ADC==========#
# creation d'un objet channel 0 de l'objet ADC MCP3008 
# un channel est une entrée analogique, le MCP3008 peut en avoir jusqu'à 8
channel_anemometre = MCP3008(0)

#==========SETUP VALUES==========#

maxVent = 0
temporisationEnvoi = 5 #temps entre deux publications de vent
temporisationReleves = 5

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
    if topic == topicAnemometreSetup:
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


ip_adress ="172.20.10.2"
port=1883
mqtt_client.connect(ip_adress, port)

topicAnemometreValeurs ='grange/sensors/anemometre/value'
topicAnemometreSetup ='grange/sensors/anemometre/setup'

mqtt_client.loop_start()
mqtt_client.subscribe(topicAnemometreValeurs)
mqtt_client.subscribe(topicAnemometreSetup)

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
mqtt_client.publish(topicAnemometreSetup, "SETUP")

while True:

    valeurVent = releveVent(temporisationReleves)
    dictionnaireMessage = {"groupe":"grange","capteur": "anemometre","valeuMoyenne": valeurVent ,"date":str(datetime.datetime.now())}
    #exemple de reglage :     dictionnaireParametres = {"groupe":"grange","capteur": "anemometre","valeurMin": 0.0 , "valeurMax": 20.0 ,"date":str(datetime.datetime.now())}

    jsonMessage = json.dumps(dictionnaireMessage)

    mqtt_client.publish(topicAnemometreValeurs,jsonMessage)
    sleep(temporisationEnvoi)
