#include <Adafruit_MAX31865.h>
#include "WiFi.h"
#include "PubSubClient.h"

// Définition des pins d'entrées/sorties
const uint8_t CAPTEUR_TEMPERATURE_PIN = 5;
const uint8_t CAPTEUR_HUMIDITE_PIN = 34;
const uint8_t SELECTEUR_VENTILATION_COMMANDE_PIN = 32;  // 0 = Arrêt; 1 = Marche
const uint8_t SELECTEUR_MOTORISATION_MODE_PIN = 33;  // 0 = Mode Manuel; 1 = Mode Automatique
const uint8_t SELECTEUR_VENTILATION_MODE_PIN = 25;  // 0 = Mode Manuel; 1 = Mode Automatique
const uint8_t MOTEUR_A_DIRECTION_PIN = 27;  // 0 = Sens positif; 1 = Sens négatif (mode automatique)
const uint8_t MOTEUR_B_DIRECTION_PIN = 14;  // 0 = Sens positif; 1 = Sens négatif (mode automatique)
const uint8_t MOTEUR_A_VITESSE_PIN = 12;  // 0 = Arrêt; 1 = Vitesse max (mode automatique); PWM
const uint8_t MOTEUR_B_VITESSE_PIN = 13;  // 0 = Arrêt; 1 = Vitesse max (mode automatique); PWM
const uint8_t VOYANT_MQTT_PIN = 36;  // 0 = Eteint (connecté); 1 = Allumé (pas de communication); clignotant = connexion
const uint8_t VOYANT_WIFI_PIN = 2;   // 0 = Eteint (connecté); 1 = Allumé (pas de communication); clignotant = connexion

const uint8_t MOTEUR_A_FC_BAS = 0;
const uint8_t MOTEUR_A_FC_HAUT = 0;
const uint8_t MOTEUR_B_FC_BAS = 0;
const uint8_t MOTEUR_B_FC_HAUT = 0;

// La valeur de la résistance Rref. Utiliser 430.0 pour PT100 et 4300.0 pour PT1000
#define RREF 430.0

// La valeur 'nominale' de resistance de la sonde pour 0°C
// 100.0 pour PT100, 1000.0 pour PT1000
#define RNOMINAL 100.0

Adafruit_MAX31865 _thermo = Adafruit_MAX31865(CAPTEUR_TEMPERATURE_PIN);

// WiFi 
const char *_ssid = "ElColoc"; // Entrez votre SSID WiFi  
const char *_motDePasse = "ASXzdc123*"; // Entrez votre mot de passe WiFi 

// MQTT Broker  
const char *_mqttBroker = ""; 
const char *_topic = ""; 
const char *_mqttUtilisateur = ""; 
const char *_mqttMotDePasse = ""; 
const int _mqttPort = 1883; 

WiFiClient _espClient; 
PubSubClient client(_espClient);

void definitionEntreesSorties() {
  // par défaut les modes des pins sont des entrées (INPUT)
  pinMode(MOTEUR_A_DIRECTION_PIN, OUTPUT);
  pinMode(MOTEUR_B_DIRECTION_PIN, OUTPUT);
  pinMode(MOTEUR_A_VITESSE_PIN, OUTPUT);
  pinMode(MOTEUR_B_VITESSE_PIN, OUTPUT);
  pinMode(VOYANT_MQTT_PIN, OUTPUT);
  pinMode(VOYANT_WIFI_PIN, OUTPUT);
}

// Connexion au réseau WiFi
// TODO : Ajouter une limite de temps
void connexionWiFi() {
  WiFi.begin(_ssid, _motDePasse);
  bool etatVoyant = false;
  while (WiFi.status() != WL_CONNECTED) { 
    delay(500); 
    //Serial.println("Connecting to WiFi..");
    digitalWrite(VOYANT_WIFI_PIN, etatVoyant);
    etatVoyant = !etatVoyant;
  }
  digitalWrite(VOYANT_WIFI_PIN, true);
}

// Connexion au réseau MQTT
// TODO : Ajouter une limite de temps
void connexionMQTT() {
  client.setServer(_mqttBroker, _mqttPort); 
  client.setCallback(callback); 
  bool etatVoyant = false;
  while (!client.connected()) { 
    delay(500); 
    //Serial.println("Connecting to MQTT..");
    digitalWrite(VOYANT_MQTT_PIN, etatVoyant);
    etatVoyant = !etatVoyant;
  }
  digitalWrite(VOYANT_MQTT_PIN, true); 
}

// Commande un moteur en direction et en vitesse (pourcentage de la vitesse max)
void commandeMoteur(uint8_t pinDirection, uint8_t pinVitesse, bool direction, uint8_t vitessePourcent) {
  uint8_t vitessePWM = (uint8_t) map(constrain(vitessePourcent, 0, 100), 0, 100, 0, 255); // Convertit la vitesse en pourcentage sur une plage analogique pour le PWM
  digitalWrite(pinDirection, direction);
  analogWrite(pinVitesse, vitessePWM);
}

// TODO : Ajouter alerte si limite de temps dépassée
bool origineMoteurs() {
  if (!digitalRead(MOTEUR_A_FC_BAS)){commandeMoteur(MOTEUR_A_DIRECTION_PIN, MOTEUR_A_VITESSE_PIN, 1, 20);}
  while (!digitalRead(MOTEUR_A_FC_BAS)){}
  commandeMoteur(MOTEUR_A_DIRECTION_PIN, MOTEUR_A_VITESSE_PIN, 1, 0);
  if (!digitalRead(MOTEUR_B_FC_BAS)){commandeMoteur(MOTEUR_B_DIRECTION_PIN, MOTEUR_B_VITESSE_PIN, 1, 20);}
  while (!digitalRead(MOTEUR_B_FC_BAS)){}
  commandeMoteur(MOTEUR_B_DIRECTION_PIN, MOTEUR_B_VITESSE_PIN, 1, 0);
  return true;
}

 // Reception du message MQTT 
void callback(char *topic, byte *payload, unsigned int length) { 

}

// Retourne la valeur moyenne en %RH de l'humidité de la serre
float acquisitionHumidite() {
  uint16_t humidite = 0;
  uint8_t echantillonage = 3;
  for (uint8_t i = 0, i < echantillonage, i++) {
    humidite += analogReadMilliVolts(CAPTEUR_HUMIDITE_PIN);
    delay(2000);
  }
  return (0.03892*(humidite/echantillonage)) - 42.017;
}

// Retourne la valeur moyenne en %RH de l'humidité de la serre
float acquisitionTemperature() {
  uint16_t temperature = 0;
  uint8_t echantillonage = 3;
  for (uint8_t i = 0, i < echantillonage, i++) {
    temperature += _thermo.temperature(RNOMINAL, RREF)
    delay(2000);
  }
  return temperature/echantillonage;
}

void setup() {
  definitionEntreesSorties();
  _thermo.begin(MAX31865_3WIRE);  // mettre 2WIRE ou 4WIRE en fonction du besoin
  connexionWiFi();
  connexionMQTT();
  origineMoteurs();

}

void loop() {
  // Vérifier la connexion au réseau WiFi
  if (WiFi.status() != WL_CONNECTED) {connexionWiFi();}

  // Vérifier la connexion au broker MQTT
  if (!client.connected()) {connexionMQTT();}

  // Lire et traiter les valeurs des capteurs

}
