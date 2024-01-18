
#include "MCP23S17.h"
#include "SPI.h"
//https://github.com/RobTillaart/MCP23S17/tree/master/examples

MCP23S17 MCP(4); //D4
int rv = 0;

void setup()
{
  pinMode(2, OUTPUT);

  Serial.begin(115200);

  SPI.begin();
  rv = MCP.begin();
  Serial.println(rv ? "true" : "false");

 
  rv = MCP.pinMode8(0, 0x00); //La ou on a les resistances (mode read)
  Serial.println(rv);
  rv = MCP.pinMode8(1, 0x00); //(mode write)
  Serial.println(rv);


  Serial.print("HWSPI: ");
  Serial.println(MCP.usesHWSPI());

  Serial.println("TEST read1(pin)");
   }


void loop()
{
  digitalWrite(2, LOW);
  delay(1000);
  digitalWrite(2, HIGH);  // turn the LED on (HIGH is the voltage level)
    delay(1000);
  for (int pin = 1; pin < 16; pin++)
  {
    MCP.write1(0, i % 2);  //  alternating HIGH/LOW
    
    delay(100);
    
    
 
  }
  

}
