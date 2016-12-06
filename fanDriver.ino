int thermo1 = A0;
int thermo2 = A1;
int thermo3 = A2;
int thermo4 = A3;
int thermo5 = A4;
int thermo6 = A5;
int fanDriver = 11;
void setup() {
  pinMode(thermo1, INPUT);
  pinMode(thermo2, INPUT);
  pinMode(thermo3, INPUT);
  pinMode(thermo4, INPUT);
  pinMode(thermo5, INPUT);
  pinMode(thermo6, INPUT);
  pinMode(fanDriver, OUTPUT);
}

void loop() {
  thermoAverage = (analogRead(thermo1) + analogRead(thermo2) + analogRead(thermo3) + analogRead(thermo4) + analogRead(thermo5) + analogRead(thermo6)) / 6;
  analogWrite(fanDriver, 255 * (thermoAverage / 200));
}
