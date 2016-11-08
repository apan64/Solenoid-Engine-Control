int x = 0;
void setup() {
  // put your setup code here, to run once:
  pinMode(3, INPUT);
  pinMode(2, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  if(digitalRead(3)){
    digitalWrite(2, HIGH);
  }
  else{
    digitalWrite(2, LOW);
  }


  
//  if(x% 2 == 0){
//    digitalWrite(9, HIGH);
//  }
//  else{
//    digitalWrite(9, LOW);
//  }
//  x++;
//  delay(100);
}
