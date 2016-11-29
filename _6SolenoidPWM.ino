// need to determine which arduino pins are actually capable of analog outputs
int solenoid1 = 3;
int solenoid2 = 5;
int solenoid3 = 6;
int solenoid4 = 9;
int solenoid5 = 10;
int solenoid6 = 11;
int buttonInput = 8;
boolean buttonPressed = false;
int encoder = A0;
//int encoder2 = A1;
//int encoder3 = A2;
//int encoder4 = A3;
//int encoder5 = A4;
//int encoder6 = A5;
int startRotationRange1 = 505;
int endRotationRange1 = 900;
int startRotationRange2 = 505;
int endRotationRange2 = 900;
int startRotationRange3 = 505;
int endRotationRange3 = 900;
unsigned long startTime;
unsigned long curTime;
long baseTime = 1000/3;
long baseActivePeriod = 300/3;
boolean lastActive;
unsigned long lastActiveTime = 0;
long lastRead = 0;
long readDelay = 10;
int potentiometer = A1;
int potentiometerMin = 0;
int potentiometerMax = 1023; // need to determine min and max values for potentiometer input

void setup() {
  Serial.begin(9600);
  pinMode(solenoid1, OUTPUT);
  pinMode(solenoid2, OUTPUT);
  pinMode(solenoid3, OUTPUT);
  pinMode(solenoid4, OUTPUT);
  pinMode(solenoid5, OUTPUT);
  pinMode(solenoid6, OUTPUT);
  pinMode(encoder, INPUT);
  pinMode(buttonInput, INPUT);
  pinMode(potentiometer, INPUT);
  startTime = millis();
  lastActive = false;
}

void loop() {
  curTime = millis() - startTime;
  int rotation = analogRead(encoder);
  int pot = analogRead(potentiometer);
  // creating an alternative button control to make system wait until a button is pressed before beginning
  if(!buttonPressed){
    if(digitalRead(buttonInput)){
      buttonPressed = true;
    }
  }
else{
  if(rotation > startRotationRange1 && rotation < endRotationRange1){
    analogWrite(solenoid1, 255 * (pot - potentiometerMin) / (potentiometerMax - potentiometerMin));
    analogWrite(solenoid2, 0);
    analogWrite(solenoid3, 0);
    analogWrite(solenoid4, 0);
    analogWrite(solenoid5, 0);
    analogWrite(solenoid6, 255 * (pot - potentiometerMin) / (potentiometerMax - potentiometerMin));
  }
  else if(rotation > startRotationRange2 && rotation < endRotationRange2){
    analogWrite(solenoid1, 0);
    analogWrite(solenoid2, 255 * (pot - potentiometerMin) / (potentiometerMax - potentiometerMin));
    analogWrite(solenoid3, 0);
    analogWrite(solenoid4, 0);
    analogWrite(solenoid5, 255 * (pot - potentiometerMin) / (potentiometerMax - potentiometerMin));
    analogWrite(solenoid6, 0);
  }
  else if(rotation > startRotationRange3 && rotation < endRotationRange3){
    analogWrite(solenoid1, 0);
    analogWrite(solenoid2, 0);
    analogWrite(solenoid3, 255 * (pot - potentiometerMin) / (potentiometerMax - potentiometerMin));
    analogWrite(solenoid4, 255 * (pot - potentiometerMin) / (potentiometerMax - potentiometerMin));
    analogWrite(solenoid5, 0);
    analogWrite(solenoid6, 0);
  }
}
  
}
