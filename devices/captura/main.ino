#include "BluetoothSerial.h"

BluetoothSerial SerialBT;

const int emgPin = 36;

void setup() {
  Serial.begin(115200);
  SerialBT.begin("EMG");
  delay(100);
  pinMode(34, INPUT);
  pinMode(35, INPUT);
}

void loop() {
  int emg=0, _emg=0;
  if(digitalRead(34)==0 && digitalRead(35)==0) {
    for(int i=0;i<10;i++) {
      _emg = _emg+analogRead(emgPin);
      delayMicroseconds(500);   // ~2000 Hz
    }
    emg = _emg/10;
  }
  // SerialBT.println(emg);
  Serial.print("2800,800,");
  Serial.println(emg);
  //delayMicroseconds(500);   // ~2000 Hz
  delay(100);
}