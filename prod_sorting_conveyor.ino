#include <Servo.h>

// Motor pins
const int motorConvayerF = 8;
const int motorConvayerB = 9;
const int motorArm1 = 10;
const int motorArm2 = 11;

//Buzzer pin
int buzzer = 5;

// IR sensor pin
const int irSensorPin = 6;
int count = 0;


void startConveyor() {
  digitalWrite(motorConvayerF, LOW);
  digitalWrite(motorConvayerB, HIGH);
}

void stopConveyor() {
  digitalWrite(motorConvayerF, LOW);
  digitalWrite(motorConvayerB, LOW);
}

void pushLeft() {
  digitalWrite(motorArm1, HIGH);
  digitalWrite(motorArm2, LOW);
  delay(1000);
  digitalWrite(motorArm1, LOW);
  digitalWrite(motorArm2, HIGH);
  delay(1000);
  digitalWrite(motorArm1, LOW);
  digitalWrite(motorArm2, LOW);
}

void pushRight() {
  digitalWrite(motorArm1, LOW);
  digitalWrite(motorArm2, HIGH);
  delay(2000);
  digitalWrite(motorArm1, HIGH);
  digitalWrite(motorArm2, LOW);
  delay(2000);
  digitalWrite(motorArm1, LOW);
  digitalWrite(motorArm2, LOW);
}

void setup() {
  pinMode(motorConvayerF, OUTPUT);
  pinMode(motorConvayerB, OUTPUT);
  pinMode(motorArm1, OUTPUT);
  pinMode(motorArm2, OUTPUT);
  pinMode(buzzer, OUTPUT);
  
  pinMode(irSensorPin, INPUT);
  
  digitalWrite(buzzer, HIGH);
  Serial.begin(9600);
  startConveyor();
}

void loop() {
  if (digitalRead(irSensorPin) == LOW && count==0) {
      stopConveyor();
      count=count+1;
      //Serial.println(count);
  } else {
    //delay(2000);
    startConveyor();
    count=0;
    delay(2000);
  }

  if (Serial.available() > 0) {
  
    String command = Serial.readStringUntil('\n');
    command.trim(); // Remove any trailing newline characters

    if (command == "LEFT") {
      //delay(2000);
      startConveyor();
      delay(2000);
      pushLeft();
    } else if (command == "RIGHT") {
      //delay(2000);
      startConveyor();
      delay(2000);
      pushRight();
    }
  }
  delay(500);
}
