int solenoid = 2;
int buttonInput = 3;
boolean buttonPressed = false;
int encoder = A0;
int startRotationRange = 505;
int endRotationRange = 900;
unsigned long startTime;
unsigned long curTime;
long baseTime = 1000/3;
long baseActivePeriod = 300/3;
boolean lastActive;
unsigned long lastActiveTime = 0;

void setup() {
  Serial.begin(9600);
  pinMode(solenoid, OUTPUT);
  pinMode(encoder, INPUT);
  pinMode(buttonInput, INPUT);
  startTime = millis();
  lastActive = false;
}

void loop() {
  curTime = millis() - startTime;
  int rotation = analogRead(encoder);
  Serial.println(rotation);
  // creating an alternative button control to make system wait until a button is pressed before beginning
  if(!buttonPressed){
    if(digitalRead(buttonInput)){
      buttonPressed = true;
    }
  }
else{
//  if(curTime < 3000){                           // start rotating at one rotation per second to have initial velocity
//    if((curTime % baseTime) < baseActivePeriod){// solenoid active for a third of the time
//      digitalWrite(solenoid, HIGH);
//    }
//    else{
//      digitalWrite(solenoid, LOW);
//    }
//  }
//  else{
    if(rotation > startRotationRange && rotation < endRotationRange){ // check to see that shaft is in rotation range to activate solenoid
//      if(!lastActive){                          // keep track of the last state of the solenoid (active, inactive)
//        lastActive = true;
//        if((millis() - lastActiveTime) < 30){   // setting control to limit upper rpm
//          Serial.println("Waiting, too fast");
//        }
//        lastActiveTime = millis();              // mark the time solenoid switched from inactive to active
//      }
      digitalWrite(solenoid, HIGH);
    }
    else{
      digitalWrite(solenoid, LOW);
      lastActive = false;
    }
//  }
}
  
}
