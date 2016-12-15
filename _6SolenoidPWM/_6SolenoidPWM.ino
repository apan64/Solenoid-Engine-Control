// need to determine which arduino pins are actually capable of analog outputs
int solenoid1 = 3; // solenoids 3+4
int solenoid2 = 5; // solenoids 2+5
int solenoid3 = 6; // solenoids 1+6
//int solenoid4 = 9;
//int solenoid5 = 10;
//int solenoid6 = 11;
int buttonInput = 8;
boolean buttonPressed = false;
int encoder = A0;
int thermocouple = A1;
int fans = 9;
//int encoder2 = A1;
//int encoder3 = A2;
//int encoder4 = A3;
//int encoder5 = A4;
//int encoder6 = A5;


int startRotationRange1 = 765; //start high -> end low or start low -> end high?
//int endRotationRange1 = 512;
int endRotationRange1 = 230;
//int endRotationRange1 = 682;
//int endRotationRange1 = 340;

int startRotationRange2 = 205;
//int endRotationRange2 = 853;
int endRotationRange2 = 630;
//int endRotationRange2 = 1023;
//int endRotationRange2 = 681;

int startRotationRange3 = 400;
//int endRotationRange3 = 171;
int endRotationRange3 = 815;
//int endRotationRange3 = 341;
//int endRotationRange3 = 1023; // control code for firing solenoid 3 has to change if it doesn't loop around 1023!

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
long rpmTime = 0;
bool lastRPMMeasure = true;
int rpm = 0;
int desired_rpm = 10;
float error;
float output = 1.0;


float integral = 0.0;
float KP = 0.5;// Proportional constant
float KI = 0.2;// Integral constant



void setup() {
  Serial.begin(9600);
  pinMode(solenoid1, OUTPUT);
  pinMode(solenoid2, OUTPUT);
  pinMode(solenoid3, OUTPUT);
  pinMode(encoder, INPUT);
  pinMode(buttonInput, INPUT);
  pinMode(potentiometer, INPUT);
  pinMode(fans, OUTPUT);
  startTime = millis();
  lastActive = false;
}

void parseString(String input){
  if (input.substring(0,3) == "rpm"){
    desired_rpm = (input.substring(4)).toInt();
    };
  }

void loop() {
  analogWrite(fans, 255 * analogRead(thermocouple / 200));
  //Listen for serial input here
  if (Serial.available() > 0) {
  parseString(Serial.readString());}

  curTime = millis() - startTime;
  int rotation = analogRead(encoder);
  Serial.println(rotation);
  int pot = analogRead(potentiometer);

  if(lastRPMMeasure && (rotation > 500)){
    rpm = 60000/(curTime-rpmTime);
//    Serial.println(rpm); // print rpm to serial

//    error = (desired_rpm - rpm) / desired_rpm;
//    if (abs(error)>0.25){
//  integral = 0;    
//} else {
//    integral = integral + (error*(curTime-rpmTime)/1000);
//  }

//    output = KP*error + KI*integral; //our output needs to be between 0 and 1

//      if (output > 1.0) {
//        output = 1.0;
//        } else if (output < 0.0) {
//          output = 0.0;
//          }
          
      output = 1.0;

   
    rpmTime = curTime;
  }
  if(rotation > 500){
    lastRPMMeasure = false;
  }
  else if(rotation < 500){
    lastRPMMeasure = true;
  }

if(endRotationRange1 > startRotationRange1){
  if(rotation > startRotationRange1 && rotation < endRotationRange1){
    Serial.println("running 1");
    analogWrite(solenoid1, (int) (255 * output));
  } else {
    analogWrite(solenoid1,0);
    }
}
else{
  if(rotation > startRotationRange1 || rotation < endRotationRange1){
    Serial.println("running 1");
    analogWrite(solenoid1, (int) (255 * output));
  }
  else{
    analogWrite(solenoid1, 0);
  }
}
  
if(endRotationRange2 > startRotationRange2){
  if(rotation > startRotationRange2 && rotation < endRotationRange2){
    Serial.println("running 2");
    analogWrite(solenoid2, (int) (255 * output));
  } else {
    analogWrite(solenoid2,0);
    }
}
else{
  if(rotation > startRotationRange2 || rotation < endRotationRange2){
    Serial.println("running 2");
    analogWrite(solenoid2, (int) (255 * output));
  }
  else{
    analogWrite(solenoid2, 0);
  }
}
if(endRotationRange3 > startRotationRange3){
  if(rotation > startRotationRange3 && rotation < endRotationRange3){
    Serial.println("running 3");
    analogWrite(solenoid3, (int) (255 * output));
  } else {
    analogWrite(solenoid3,0);
    }
}
else{
  if(rotation > startRotationRange3 || rotation < endRotationRange3){
    Serial.println("running 3");
    analogWrite(solenoid3, (int) (255 * output));
  }
  else{
    analogWrite(solenoid3, 0);
  }
}
}
