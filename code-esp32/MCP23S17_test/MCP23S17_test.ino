//
//    FILE: MCP23S17_digitalWrite.ino
//  AUTHOR: Rob Tillaart
// PURPOSE: test MCP23S17 library
//     URL: https://github.com/RobTillaart/MCP23S17


#include "MCP23S17.h"
#include "SPI.h"

MCP23S17 MCP(4);   //  SW SPI   address 0x00
int bp_pin = 7;
int led_pin = 8;
int bp_etat = 0;


void setup()
{
  Serial.begin(115200);
  
  Serial.println();
  Serial.print("MCP23S17_LIB_VERSION: ");
  delay(1000);
  Serial.println(MCP23S17_LIB_VERSION);
  delay(100);

  SPI.begin();
  bool b = MCP.begin();
  Serial.println(b ? "true" : "false");
  delay(100);

  MCP.pinMode8(0, 0xFF);      //  0 = output , 1 = input
  MCP.pinMode8(1, 0x00);
  MCP.setPolarity8(0, 0xFF);  // 0 = NC, 1 = NO

}


void loop()
{
  delay(500);

  bp_etat = MCP.read1(bp_pin);  
  Serial.printf("etat bouton : %d \n", bp_etat);
  MCP.write1(led_pin,bp_etat);

}


//  -- END OF FILE --

