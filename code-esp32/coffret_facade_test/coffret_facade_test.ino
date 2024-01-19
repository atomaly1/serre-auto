//
//    FILE: MCP23S17_digitalWrite.ino
//  AUTHOR: Rob Tillaart
// PURPOSE: test MCP23S17 library
//     URL: https://github.com/RobTillaart/MCP23S17


#include "MCP23S17.h"
#include "SPI.h"

MCP23S17 MCP(4);   //  SW SPI   address 0x00
int bp_pin = 1;
int led_pin = 9;
int bp_etat = 0;
int var = 0;


void setup()
{
  delay(5000);

  Serial.begin(115200);
  

  SPI.begin();
  delay(100);

  bool b = MCP.begin();
  delay(100);

  pinMode(2, OUTPUT);

  MCP.pinMode8(0, 0xFF);      //  0x00 = output , 0xFF = input
  //MCP.pinMode1(0, 1);      //  0 = output , 1 = input
  MCP.pinMode8(1, 0x00);
  //MCP.setPolarity8(0, 0x00);  // 0 = NC, 1 = NO
  //MCP.setPullup8(0, 0xFF); //0= maintien  

}



void blink_all(){

  
  digitalWrite(2, LOW);
  MCP.write8(1,0xFF);
  delay(2000);
  MCP.write8(1, 0x00);
  digitalWrite(2, HIGH);
  delay(2000);

}



void blink_led(){

  MCP.write1(led_pin, 1);
  digitalWrite(2, LOW);
  delay(2000);
  MCP.write1(led_pin, 0);
  digitalWrite(2, HIGH);
  delay(2000);

}

void in_and_out(){
  var = MCP.read8(0);
  delay(10);
  MCP.write8(1,var);
}




void loop()
{
  //blink_led();
  //bp_etat = MCP.read1(bp_pin);  
  // digitalWrite(2, bp_etat);


  // // //Serial.printf("etat bouton : %d \n", bp_etat);
  // MCP.write1(led_pin,bp_etat);

  // if (!MCP.read1(bp_pin)){
  //   blink_all();
  // }


  in_and_out();

  delay(50);
}


//  -- END OF FILE --

