// V = voyant; BP = bouton poussoir; S = sélecteur; FC = fin de course; CS = chip select; ES = entrée/sortie; TEMP = température

// Alimentation ? https://docs.ai-thinker.com/_media/nodemcu32-s_specification_v1.3.pdf p.13

#include "SPI.h"
#include "WiFi.h"
#include "PubSubClient.h" 
#include "MCP23S17.h" // Rob Tillaart
#include "CytronMotorDriver.h"
#include <Adafruit_MAX31865.h>

// Définition des pins d'entrées/sorties
const uint8_t MOTEUR_A_FC_BAS         = 13;
const uint8_t MOTEUR_A_FC_HAUT        = 12;
const uint8_t MOTEUR_B_FC_BAS         = 14;
const uint8_t MOTEUR_B_FC_HAUT        = 27;
const uint8_t MOTEUR_A_DIRECTION_PIN  = 25;  // 0 = Sens positif; 1 = Sens négatif (mode automatique)
const uint8_t MOTEUR_A_VITESSE_PIN    = 26;  // 0 = Arrêt; 1 = Vitesse max (mode automatique); PWM
const uint8_t MOTEUR_B_DIRECTION_PIN  = 32;  // 0 = Sens positif; 1 = Sens négatif (mode automatique)
const uint8_t MOTEUR_B_VITESSE_PIN    = 33;  // 0 = Arrêt; 1 = Vitesse max (mode automatique); PWM
const uint8_t CAPTEUR_HUMIDITE_A_PIN  = 35;
const uint8_t CAPTEUR_HUMIDITE_B_PIN  = 34;

// CHIP SELECT pour la communication SPI
const uint8_t  MODULE_ES_CS     = 4;  // Module d'entrées/sorties MCP23S17
const uint8_t  MODULE_TEMP_A_CS = 2;  // Amplificateur de sonde de température PT100 MAX31865
const uint8_t  MODULE_TEMP_B_CS = 15; // Amplificateur de sonde de température PT100 MAX31865

// 0 = arrêt de sécurité; 1 = initialisation; 2 = marche normale; 3 = mode dégradé 
#define ARRET_SECURITE  0
#define INITIALISATION  1
#define MARCHE_NORMALE  2
#define MODE_DEGRADE    3

#define MARCHE_LENTE    127
#define MARCHE_RAPIDE   255
#define ARRET      0
#define MONTER     1
#define DESCENDRE -1

#define ENTREES 0
#define SORTIES 1

// La valeur de la résistance Rref. Utiliser 430.0 pour PT100 et 4300.0 pour PT1000
#define RREF 430.0

// La valeur 'nominale' de resistance de la sonde pour 0°C
// 100.0 pour PT100, 1000.0 pour PT1000
#define RNOMINAL 100.0

Adafruit_MAX31865 _thermoA = Adafruit_MAX31865(MODULE_TEMP_A_CS);
Adafruit_MAX31865 _thermoB = Adafruit_MAX31865(MODULE_TEMP_B_CS);

MCP23S17 _MODULE_ES(MODULE_ES_CS);

CytronMD _moteurA(PWM_DIR, MOTEUR_A_VITESSE_PIN, MOTEUR_A_DIRECTION_PIN);
CytronMD _moteurB(PWM_DIR, MOTEUR_B_VITESSE_PIN, MOTEUR_B_DIRECTION_PIN);

// WiFi 
const char *_ssid = "Alban";          // Entrez votre SSID WiFi  
const char *_motDePasse = "11111110"; // Entrez votre mot de passe WiFi 

// MQTT Broker  
const char *_mqttBroker = "172.20.10.4"; 
const char *_topic = "";  
const int _mqttPort = 1883; 

WiFiClient _espClient; 
PubSubClient client(_espClient);

uint8_t _etatMachine; // 0 = arrêt de sécurité; 1 = marche normale; 2 = mode dégradé; 3 = initialisation
bool _erreur;
unsigned long _deltaTempsMesure;
unsigned long _timeoutMoteurs;

// Variables globales
uint8_t module_ES_Entrees, module_ES_Sorties;
bool aeration_Mode_S, ventilation_Mode_S;
bool moteurA_Monter_BP, moteurA_Descendre_BP, moteurB_Monter_BP, moteurB_Descendre_BP;
bool moteurA_FC_Haut, moteurA_FC_Bas, moteurB_FC_Haut, moteurB_FC_Bas;
bool ventilation_MarcheArret_S;
bool acquittement_BP;

bool acquitter;
bool ventilation_Etat; // 0 = Arrêt, 1 = Marche
uint8_t moteurA_Etat; // 0 = Arrêt; 1 = Monter; 2 = Descendre
uint8_t moteurB_Etat; // 0 = Arrêt; 1 = Monter; 2 = Descendre

bool etatOrigineMoteur; // 0 = l'origine moteur n'a pas encore été effectuée; 1 = origine effectuée

unsigned long duree_MoteurA_Marche;
unsigned long duree_MoteurB_Marche;
unsigned long temps_actuel_Moteurs;

void definitionEntreesSorties() {
  // par défaut les modes des pins sont des entrées (INPUT)
  pinMode(MOTEUR_A_DIRECTION_PIN, OUTPUT);
  pinMode(MOTEUR_B_DIRECTION_PIN, OUTPUT);
  pinMode(MOTEUR_A_VITESSE_PIN, OUTPUT);
  pinMode(MOTEUR_B_VITESSE_PIN, OUTPUT);

  pinMode(MOTEUR_A_FC_BAS, INPUT);
  pinMode(MOTEUR_A_FC_HAUT, INPUT);
  pinMode(MOTEUR_B_FC_BAS, INPUT);
  pinMode(MOTEUR_B_FC_HAUT, INPUT);
}

void initialisationVariables() {
  module_ES_Entrees = 0x00;
  module_ES_Sorties = 0x00;
  etatOrigineMoteur = false;
  _timeoutMoteurs = 2 * 60 * 1000; // temps maximal d'allumage d'un moteur en millisecondes
}

// Connexion au réseau WiFi
// TODO : Ajouter une limite de temps
void connexionWiFi() {
  WiFi.begin(_ssid, _motDePasse);
  while (WiFi.status() != WL_CONNECTED) { 
    delay(500); 
    Serial.println("Connecting to WiFi..");
  }
}

// Connexion au réseau MQTT
// TODO : Ajouter une limite de temps
void connexionMQTT() {
  client.setServer(_mqttBroker, _mqttPort); 
  client.setCallback(callback); 
  while (!client.connected()) { 
    delay(500); 
    Serial.println("Connecting to MQTT..");
  }
}

// TODO : Ajouter alerte si limite de temps dépassée + gestion des erreurs
bool origineMoteurs() {
  Serial.print("Origine Moteurs : MoteurA ");
  if (!digitalRead(MOTEUR_A_FC_BAS)){_moteurA.setSpeed(MARCHE_RAPIDE * DESCENDRE);}
  while (!digitalRead(MOTEUR_A_FC_BAS)){delay(500);}
  _moteurA.setSpeed(ARRET);
  Serial.print("MoteurB ");
  if (!digitalRead(MOTEUR_B_FC_BAS)){_moteurB.setSpeed(MARCHE_RAPIDE * DESCENDRE);}
  while (!digitalRead(MOTEUR_B_FC_BAS)){delay(500);}
  _moteurB.setSpeed(ARRET);
  etatOrigineMoteur = true;
  Serial.println("OK");
  return true; // true si pas d'erreur, sinon false
}

 // Reception du message MQTT 
void callback(char *topic, byte *payload, unsigned int length) { 
  Serial.println("Callback MQTT");

}

// Retourne la valeur moyenne en %RH de l'humidité de la serre
float acquisitionHumidite() {
  Serial.print("Acquisition Humidité : ");
  uint16_t humiditeA = 0;
  uint16_t humiditeB = 0;
  uint16_t humidite = 0;
  uint8_t echantillonage = 3;
  for (uint8_t i = 0; i < echantillonage; i++) {
    humiditeA += analogReadMilliVolts(CAPTEUR_HUMIDITE_A_PIN);
    //humiditeB += analogReadMilliVolts(CAPTEUR_HUMIDITE_B_PIN);
    delay(2000);
  }
  humiditeB = humiditeA;
  humidite = (0.03892*0.5*(humiditeA+humiditeB)/echantillonage) - 42.017;
  Serial.println(humidite);
  return humidite;
}

// Retourne la valeur moyenne en °C de la température de la serre
float acquisitionTemperature() {
  Serial.print("Acquisition Température : ");
  uint16_t temperatureA = 0;
  uint16_t temperatureB = 0;
  uint16_t temperature = 0;
  uint8_t echantillonage = 3;
  for (uint8_t i = 0; i < echantillonage; i++) {
    temperatureA += _thermoA.temperature(RNOMINAL, RREF);
    //temperatureB += _thermoB.temperature(RNOMINAL, RREF);
    delay(2000);
  }
  temperatureB = temperatureA;
  temperature = 0.5 * (temperatureA + temperatureB) / echantillonage;
  Serial.println(temperature);
  return temperature;
}

void lireEntrees() {
  Serial.print("---LECTURE DES ENTREES---");
  moteurA_FC_Haut   = digitalRead(MOTEUR_A_FC_HAUT);
  moteurA_FC_Bas    = digitalRead(MOTEUR_A_FC_BAS);
  moteurB_FC_Haut   = digitalRead(MOTEUR_B_FC_HAUT);
  moteurB_FC_Bas    = digitalRead(MOTEUR_B_FC_BAS);

  // Déclaration des variables pour chaque entrée
  bool entrees[8];
  module_ES_Entrees = _MODULE_ES.read8(ENTREES);

  // Boucle pour extraire et inverser chaque bit d'entrée
  for (int i = 0; i < 8; i++) {
    entrees[i] = (module_ES_Entrees & (1 << i)) >> i;
    Serial.print(entrees[i]);
  }
  Serial.println();
  // Attribution des variables aux entrées spécifiques
  ventilation_MarcheArret_S = entrees[0];
  ventilation_Mode_S = entrees[1];
  moteurB_Descendre_BP = entrees[2];
  moteurB_Monter_BP = entrees[3];
  moteurA_Descendre_BP = entrees[4];
  moteurA_Monter_BP = entrees[5];
  aeration_Mode_S = entrees[6];
  acquittement_BP = entrees[7];
  }

void ecrireSorties() {
  Serial.print("---ECRITURE DES SORTIES--- : \nVentilation et Voyants :");
  // 7 = Marche/Arrêt Ventilation; 4 = Voyant Ventilation; 3 = Voyant moteur B; 2 = Voyant moteur A; 1 = Voyant erreur; 0 = Voyant acquitement
  module_ES_Sorties = ((ventilation_Etat << 7) | (0 << 6) | (0 << 5) | (ventilation_Etat << 4) | (((moteurB_Etat>0)?1:0) << 3) | (((moteurA_Etat>0)?1:0) << 2) | (_erreur << 1) | acquitter);
  _MODULE_ES.write8(SORTIES, module_ES_Sorties);
  Serial.println(module_ES_Sorties);
  Serial.print("Moteurs :");
  Serial.printf("A:%d B%d", moteurA_Etat, moteurB_Etat);

  switch(moteurA_Etat) {
    case 0:
      _moteurA.setSpeed(MARCHE_LENTE * ARRET);
      duree_MoteurA_Marche = 0;
      temps_actuel_Moteurs = millis();
      break;
    case 1:
      _moteurA.setSpeed(MARCHE_LENTE * MONTER);
      duree_MoteurA_Marche = millis() - temps_actuel_Moteurs;
      break;
    case 2:
      _moteurA.setSpeed(MARCHE_LENTE * DESCENDRE);
      duree_MoteurA_Marche = millis() - temps_actuel_Moteurs;
      break;
    default:
      _moteurA.setSpeed(MARCHE_LENTE * ARRET);
      duree_MoteurA_Marche = 0;
      temps_actuel_Moteurs = millis();
      break;
  }
      
  switch(moteurB_Etat) {
    case 0:
      _moteurB.setSpeed(MARCHE_LENTE * ARRET);
      break;
    case 1:
      _moteurB.setSpeed(MARCHE_LENTE * MONTER);
      break;
    case 2:
      _moteurB.setSpeed(MARCHE_LENTE * DESCENDRE);
      break;
    default:
      _moteurB.setSpeed(MARCHE_LENTE * ARRET);
      break;
  }
  /*
  if (duree_MoteurA_Marche >= timeoutMoteurs) {
    _erreur = true;
    // Serial.println("Timeout Moteur A");
  } 
  */
}

void modeManuel() {
  Serial.println("---MODE MANUEL---");
  if (moteurA_Monter_BP && !moteurA_FC_Haut && !_erreur) {
      moteurA_Etat = 1;
      } else if (moteurA_Descendre_BP && !moteurA_FC_Bas && !_erreur) {
        moteurA_Etat = 2;
        } else {moteurA_Etat = 0;}
  if (moteurB_Monter_BP && !moteurB_FC_Haut && !_erreur) {
    moteurB_Etat = 1;
    } else if (moteurB_Descendre_BP && !moteurB_FC_Bas && !_erreur) {
      moteurB_Etat = 2;
      } else {moteurB_Etat = 0;}
  if (ventilation_MarcheArret_S && !_erreur) {
    ventilation_Etat = 1;
    } else {ventilation_Etat = 0;}
}

void modeAutomatique() {
  Serial.println("---MODE AUTOMATIQUE---");
  delay(100);

}

void setup() {
  // temporisation pour que tous les composants soit bien allumés
  delay(5000);
  Serial.begin(115200);
  Serial.println("--INITIALISATION--");

  initialisationVariables();

  // Communication SPI
  SPI.begin();

  definitionEntreesSorties();
  
  _thermoA.begin(MAX31865_3WIRE);  // mettre 2WIRE ou 4WIRE en fonction du besoin
  //_thermoB.begin(MAX31865_3WIRE);  // mettre 2WIRE ou 4WIRE en fonction du besoin

  // Configuration du module d'entrées/sorties
  _MODULE_ES.begin();
  _MODULE_ES.pinMode8(ENTREES, 0xFF);      //  0x00 = output , 0xFF = input
  _MODULE_ES.pinMode8(SORTIES, 0x00);
  _MODULE_ES.setPolarity8(0, 0xFF);  // 0 = NC, 1 = NO
  
  //connexionWiFi();
  //connexionMQTT();
  origineMoteurs();
}

void loop() {
  // Vérifier la connexion au réseau WiFi
  //if (WiFi.status() != WL_CONNECTED) {connexionWiFi();}

  // Vérifier la connexion au broker MQTT
  //if (!client.connected()) {connexionMQTT();}

  if (!etatOrigineMoteur){origineMoteurs();}

  // Lecture des entrées
  lireEntrees();

  // Acquisition de la donnée

  // Récupérer les données du serveur via MQTT


  // Traitement des données

  // Mode manuel
  if (!aeration_Mode_S) {
    modeManuel();
  }
  
  // Mode automatique
  if (aeration_Mode_S) {
    modeAutomatique();
  }

  // Envoyer les données au serveur via MQTT  
  
  // Ecriture des sorties
  ecrireSorties();  

  //delay(500);
}
