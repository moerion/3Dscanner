#include <Servo.h>

Servo panServo;

// SERVO VARS
int pos = 0;
const int pulse0Degrees = 1000;   // pulse width for 0 degrees
const int pulse360Degrees = 2000;  // pulse width for 360 degrees
const int pcenter = 1000; // using 1000 for center, or 0 degrees, you may want to use something different
const int offset = 120;   // servo offset
int servoPanPin = 9;     // Control pin for servo motor

int ir[360];

int scan = 1;

int front;

//*****************************************************************************************
void setup()
{ 
  Serial.begin(115200); 
  //servo setup
  panServo.attach(servoPanPin);  

  // Default center, or close to it 
  panServo.writeMicroseconds(pcenter);	// close to center GWS125-IT/2BB/F ?  
}

//***************************************************************************************
void loop() //Main Loop
{
  
 if (scan != 0){ 
    
    for(pos = 0; pos < 360; pos += 1)  // goes from 0 degrees to 360 degrees 
    {                                  // in steps of 1 degree 
      rotateServo(pos+offset);         // tell servo to go to position in variable 'pos' + offset
      delay(20);                       // waits 20ms for the servo to reach the position 
  
        // collect sensor data for each point and calculate average
       ir[pos] = analogRead(A0);
       delay(5); 
       ir[pos] += analogRead(A0);
       delay(5); 
       ir[pos] += analogRead(A0);
       delay(5); 
       ir[pos] += analogRead(A0);
       delay(5); 
       ir[pos] += analogRead(A0);
       delay(5); 
       ir[pos] = ir[pos] / 5;
    } 
  
    front = analogRead(A1);
    delay(5);
    
    if (front < 200){
     scan = 0; 
    }
      
    // transfer data serially to computer
     Serial.print("COM:");
     for (int i = 0; i<360; i++){
     
       Serial.print(ir[i]);
       Serial.print(",");
     }
     Serial.print("SCAN:");
     Serial.print(scan);
     Serial.print(",");
     delay(10);
     
    //return servo to initial position
    rotateServo(270 + offset);
    delay(100);
    rotateServo(180 + offset);
    delay(100);
    rotateServo(90 + offset);
    delay(100);
    rotateServo(0 + offset);
    delay(100);
    
    if (scan != 0){
      scan = scan + 1;
    }
    delay(1000);
 }
}

//********************************************************************************
void rotateServo (int pos) {
  int pulse = map(pos,0,360,pulse0Degrees, pulse360Degrees);
  panServo.writeMicroseconds(pulse);
}


