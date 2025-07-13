#include <Servo.h>

#define laserPin 6
#define xPin 4
#define yPin 5

Servo servo_x;
Servo servo_y;

int angle_x, angle_y, x_data, y_data;
int sensitivity_x = 25; 
int sensitivity_y = 25; 

String pyData;

void attach_servo() {
  servo_x.attach(xPin);
  servo_y.attach(yPin);
}



void setup() {
  pinMode(laserPin, OUTPUT);
  digitalWrite(laserPin, HIGH);
  
  attach_servo();
  servo_x.write(68);
  servo_y.write(40);
  
  Serial.begin(2000000);
  Serial.setTimeout(1);
}

void loop() {
  while(!Serial.available());
  
  pyData = Serial.readString();
  x_data = pyData.substring(0, pyData.indexOf(" ")).toInt();
  y_data = pyData.substring(pyData.indexOf(" ")+1).toInt();
    
  if ((x_data + y_data) <= 3000) {
    
    angle_x = map(x_data, 0, 1920, 55, 1920/sensitivity_x + 55);
    angle_y = map(y_data, 0, 1080, 10, 1080/sensitivity_y + 10);

    servo_x.write(angle_x);
    servo_y.write(angle_y);
  }
  else {
    
    switch (x_data + y_data) {
      case 19998:   
        if (digitalRead(laserPin) == HIGH) {
          digitalWrite(laserPin, LOW);
        }
        else {
          digitalWrite(laserPin, HIGH);
        }
        break;
      case 19996: 
        digitalWrite(laserPin, LOW);
        break;
      case 19997: 
        digitalWrite(laserPin, HIGH);
        break;
    }
  }
  
  Serial.flush();
}