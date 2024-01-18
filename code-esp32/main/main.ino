// V = voyant; BP = bouton poussoir; S = sélecteur; FC = fin de course; CS = chip select; ES = entrée/sortie; TEMP = température

#include "SPI.h"
#include "WiFi.h"
#include "PubSubClient.h" // EspMQTTClient by Patrick Lapointe
#include "MCP23S17.h" // Rob Tillaart
#include "CytronMotorDriver.h"
#include <Adafruit_MAX31865.h>

// Définition des pins d'entrées/sorties
const uint8_t MOTEUR_A_FC_BAS = 13;
const uint8_t MOTEUR_A_FC_HAUT = 12;
const uint8_t MOTEUR_B_FC_BAS = 14;
const uint8_t MOTEUR_B_FC_HAUT = 27;
const uint8_t MOTEUR_A_DIRECTION_PIN = 34;  // 0 = Sens positif; 1 = Sens négatif (mode automatique)
const uint8_t MOTEUR_A_VITESSE_PIN = 35;    // 0 = Arrêt; 1 = Vitesse max (mode automatique); PWM
const uint8_t MOTEUR_B_DIRECTION_PIN = 32;  // 0 = Sens positif; 1 = Sens négatif (mode automatique)
const uint8_t MOTEUR_B_VITESSE_PIN = 33;    // 0 = Arrêt; 1 = Vitesse max (mode automatique); PWM
const uint8_t CAPTEUR_HUMIDITE_A_PIN = 26;
const uint8_t CAPTEUR_HUMIDITE_B_PIN = 25;

// CHIP SELECT pour la communication SPI
const uint8_t  MODULE_ES_CS = 4;      // Module d'entrées/sorties MCP23S17
const uint8_t  MODULE_TEMP_A_CS = 2;  // Amplificateur de sonde de température PT100 MAX31865
const uint8_t  MODULE_TEMP_B_CS = 15;  // Amplificateur de sonde de température PT100 MAX31865

#define MARCHE_LENTE 127
#define MARCHE_RAPIDE 255
#define ARRET 0
#define MONTER 1
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

CytronMD _moteurA(PWM_DIR, MOTEUR_A_VITESSE_PIN, MOTEUR_A_DIRECTION_PIN);
CytronMD _moteurB(PWM_DIR, MOTEUR_B_VITESSE_PIN, MOTEUR_B_DIRECTION_PIN);

MCP23S17 MODULE_ES(MODULE_ES_CS);

// WiFi 
const char *_ssid = "Alban";          // Entrez votre SSID WiFi  
const char *_motDePasse = "11111110"; // Entrez votre mot de passe WiFi 

// MQTT Broker  
const char *_mqttBroker = "172.20.10.4"; 
const char *_topic = "";  
const int _mqttPort = 1883; 

WiFiClient _espClient; 
PubSubClient client(_espClient);

// Variables globales
uint8_t module_ES_Entrees, module_ES_Sorties;
bool aeration_Mode_S, ventilation_Mode_S;
bool moteurA_Monter_BP, moteurA_Descendre_BP, moteurB_Monter_BP,  moteurB_Descendre_BP;
bool moteurA_FC_Haut, moteurA_FC_Bas, moteurB_FC_Haut, moteurB_FC_Bas;
bool aeration_MarcheArret_S;
bool acquittement_BP;

bool acquitter, erreur;
bool ventilation_Etat; // 0 = Arrêt, 1 = Marche
uint8_t moteurA_Etat; // 0 = Arrêt; 1 = Monter; 2 = Descendre
uint8_t moteurB_Etat; // 0 = Arrêt; 1 = Monter; 2 = Descendre

void definitionEntreesSorties() {
  // par défaut les modes des pins sont des entrées (INPUT)
  pinMode(MOTEUR_A_DIRECTION_PIN, OUTPUT);
  pinMode(MOTEUR_B_DIRECTION_PIN, OUTPUT);
  pinMode(MOTEUR_A_VITESSE_PIN, OUTPUT);
  pinMode(MOTEUR_B_VITESSE_PIN, OUTPUT);
}

void initialisationVariables() {
  module_ES_Entrees = 0x00;
  module_ES_Sorties = 0x00;
}

// Connexion au réseau WiFi
// TODO : Ajouter une limite de temps
void connexionWiFi() {
  WiFi.begin(_ssid, _motDePasse);
  while (WiFi.status() != WL_CONNECTED) { 
    delay(500); 
    //Serial.println("Connecting to WiFi..");
  }
}

// Connexion au réseau MQTT
// TODO : Ajouter une limite de temps
void connexionMQTT() {
  client.setServer(_mqttBroker, _mqttPort); 
  client.setCallback(callback); 
  while (!client.connected()) { 
    delay(500); 
    //Serial.println("Connecting to MQTT..");
  }
}

// TODO : Ajouter alerte si limite de temps dépassée + gestion des erreurs
bool origineMoteurs() {
  if (digitalRead(MOTEUR_A_FC_BAS)){_moteurA.setSpeed(MARCHE_RAPIDE * DESCENDRE);}
  while (digitalRead(MOTEUR_A_FC_BAS)){}
  _moteurA.setSpeed(ARRET);
  if (!digitalRead(MOTEUR_B_FC_BAS)){_moteurB.setSpeed(MARCHE_RAPIDE * DESCENDRE);}
  while (!digitalRead(MOTEUR_B_FC_BAS)){}
  _moteurB.setSpeed(ARRET);
  return true;
}

 // Reception du message MQTT 
void callback(char *topic, byte *payload, unsigned int length) { 

}

// Retourne la valeur moyenne en %RH de l'humidité de la serre
float acquisitionHumidite() {
  uint16_t humiditeA = 0;
  uint16_t humiditeB = 0;
  uint8_t echantillonage = 3;
  for (uint8_t i = 0; i < echantillonage; i++) {
    humiditeA += analogReadMilliVolts(CAPTEUR_HUMIDITE_A_PIN);
    humiditeB += analogReadMilliVolts(CAPTEUR_HUMIDITE_B_PIN);
    delay(2000);
  }
  return (0.03892*0.5*(humiditeA+humiditeB)/echantillonage) - 42.017;
}

// Retourne la valeur moyenne en °C de la température de la serre
float acquisitionTemperature() {
  uint16_t temperatureA = 0;
  uint16_t temperatureB = 0;
  uint8_t echantillonage = 3;
  for (uint8_t i = 0; i < echantillonage; i++) {
    temperatureA += _thermoA.temperature(RNOMINAL, RREF);
    temperatureB += _thermoB.temperature(RNOMINAL, RREF);
    delay(2000);
  }
  return 0.5 * (temperatureA + temperatureB) / echantillonage;
}

void lireEntrees() {
  moteurA_FC_Haut   = digitalRead(MOTEUR_A_FC_HAUT);
  moteurA_FC_Bas    = digitalRead(MOTEUR_A_FC_BAS);
  moteurB_FC_Haut   = digitalRead(MOTEUR_B_FC_HAUT);
  moteurB_FC_Bas    = digitalRead(MOTEUR_B_FC_BAS);
  
  module_ES_Entrees       = MODULE_ES.read8(ENTREES);
  aeration_MarcheArret_S  = (module_ES_Entrees & 0x01) >> 0; // Premier bit des entrées
  acquittement_BP         = (module_ES_Entrees & 0x02) >> 1; // Deuxième bit des entrées
  aeration_Mode_S         = (module_ES_Entrees & 0x04) >> 2; // Troisième bit des entrées
  moteurA_Monter_BP       = (module_ES_Entrees & 0x08) >> 3; // Quatrième bit des entrées
  moteurA_Descendre_BP    = (module_ES_Entrees & 0x10) >> 4; // Cinquième bit des entrées
  moteurB_Monter_BP       = (module_ES_Entrees & 0x20) >> 5; // Sixième bit des entrées
  moteurB_Descendre_BP    = (module_ES_Entrees & 0x40) >> 6; // Septième bit des entrées
  ventilation_Mode_S      = (module_ES_Entrees & 0x80) >> 7; // Huitième bit des entrées  
}

void ecrireSorties() {
  module_ES_Sorties = ((ventilation_Etat << 7) | (0 << 6) | (0 << 5) | (ventilation_Etat << 4) | (((moteurA_Etat>0)?1:0) << 3) | (((moteurB_Etat>0)?1:0) << 2) | (erreur << 1) | acquitter);
  
  switch(moteurA_Etat) {
    case 0:
      _moteurA.setSpeed(MARCHE_LENTE * ARRET);
      break;
    case 1:
      _moteurA.setSpeed(MARCHE_LENTE * MONTER);
      break;
    case 2:
      _moteurA.setSpeed(MARCHE_LENTE * DESCENDRE);
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
  }
}

void modeMANU(){
  delay(10);
 
}

void modeAUTO() {
  delay(10);

}

void setup() {
  definitionEntreesSorties();
  _thermoA.begin(MAX31865_3WIRE);  // mettre 2WIRE ou 4WIRE en fonction du besoin
  _thermoB.begin(MAX31865_3WIRE);  // mettre 2WIRE ou 4WIRE en fonction du besoin


  SPI.begin();
  MODULE_ES.begin();
  MODULE_ES.pinMode8(ENTREES, 0xFF);      //  0x00 = output , 0xFF = input
  
  MODULE_ES.pinMode8(SORTIES, 0x00);
  MODULE_ES.setPolarity8(0, 0xFF);  // 0 = NC, 1 = NO
  
  connexionWiFi();
  connexionMQTT();
  origineMoteurs();
}

void loop() {
  // Vérifier la connexion au réseau WiFi
  if (WiFi.status() != WL_CONNECTED) {connexionWiFi();}

  // Vérifier la connexion au broker MQTT
  if (!client.connected()) {connexionMQTT();}

  // Lecture des entrées
  lireEntrees();
  
  
  // Traitement des données
  
  // Ecriture des sorties
  ecrireSorties();  
}
