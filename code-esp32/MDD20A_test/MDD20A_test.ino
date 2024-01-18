 #include "CytronMotorDriver.h"

CytronMD motor1(PWM_DIR, 26, 25);  // PWM 1 = Pin 12, DIR 1 = Pin 13.

int vitesse_motor_1 = 0;

void setup() {
  delay(5000);


}

void loop() {
  vitesse_motor_1 = 128;
  motor1.setSpeed(vitesse_motor_1);   // Motor 1 runs forward at 50% speed.
  delay(5000);
  vitesse_motor_1 = -128;
  motor1.setSpeed(vitesse_motor_1);   // Motor 1 runs backward at 50% speed.
  delay(5000);


}
