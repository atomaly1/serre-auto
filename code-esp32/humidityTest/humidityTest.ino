#include <math.h>

const int humiditySensorPin = 4;
int analogVolts;

float mVToRHLin(int mV) {
  return (0.03892*mV) - 42.017;
}

float mVToRHPoly(int mV) {
  return -1.91e-9 * pow(mV, 3) + 1.33e-5 * pow(mV, 2) + 9.56e-3 * mV - 2.16e1;
}

void setup() {
  Serial.begin(115200);

  //set the resolution to 12 bits (0-4096)
  analogReadResolution(12);
}

void loop() {
  // read the analog / millivolts value for pin 2:
  analogVolts = analogReadMilliVolts(humiditySensorPin);

  Serial.print(mVToRHPoly(analogVolts));
  Serial.print(",");
  Serial.println(mVToRHLin(analogVolts));

  delay(1000);  // delay in between reads for clear read from serial


}
