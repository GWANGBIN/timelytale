#include <SoftwareSerial.h>

int Tx = 6; // Transmit pin for Bluetooth
int Rx = 7; // Receive pin for Bluetooth
SoftwareSerial BtSerial(Tx, Rx);

int state = 0;
String temp, pid2101, pid2100, pid2102_steer;
unsigned long t = 0;
bool is_timeout = false;

void setup() {
  Serial.begin(9600); // Initialize serial communication with PC
  BtSerial.begin(38400); // Initialize Bluetooth communication with OBD2
}

void loop() {
  // Handle OBD2 Bluetooth communication
  if (state == 0) {
    BtSerial.println("AT SH 7E2");
    delay(100);
    while (BtSerial.available()) {
      temp = BtSerial.readStringUntil('>');
    }
    state = 1;
  }
  else if (state == 1) {
    BtSerial.println("21012");
    delay(100);
    while (BtSerial.available()) {
      pid2101 = BtSerial.readStringUntil('>');
    }
    state = 2;
  }
  else if (state == 2) {
    BtSerial.println("21002");
    delay(100);
    while (BtSerial.available()) {
      pid2100 = BtSerial.readStringUntil('>');
    }
    state = 3;
  }
  else if (state == 3) {
    BtSerial.println("AT SH 7D4");
    delay(100);
    while (BtSerial.available()) {
      temp = BtSerial.readStringUntil('>');
    }
    state = 4;
  }
  else if (state == 4) {
    BtSerial.println("21012");
    delay(100);
    while (BtSerial.available()) {
      pid2102_steer = BtSerial.readStringUntil('>');
    }
    state = 0;
  }

  // Print OBD data to Serial Monitor
  Serial.print("Speed: ");
  Serial.print(hexToDec(pid2101.substring(54, 56)));
  Serial.print(",");

  Serial.print("Throttle: ");
  Serial.print(hexToDec(pid2101.substring(51, 53)));
  Serial.print(",");

  Serial.print("Brake: ");
  Serial.print(hexToDec(pid2100.substring(51, 53)));
  Serial.print(",");

  Serial.print("Steering: ");
  Serial.print(String(hexToDec2(pid2102_steer.substring(29, 31) + pid2102_steer.substring(36, 38))));
  Serial.println();
  
  is_timeout = false; // Reset timeout flag
}

unsigned int hexToDec(String hexString) {
  unsigned int decValue = 0;
  int nextInt;
  for (int i = 0; i < hexString.length(); i++) {
    nextInt = int(hexString.charAt(i));
    if (nextInt >= 48 && nextInt <= 57) nextInt = map(nextInt, 48, 57, 0, 9);
    if (nextInt >= 65 && nextInt <= 70) nextInt = map(nextInt, 65, 70, 10, 15);
    if (nextInt >= 97 && nextInt <= 102) nextInt = map(nextInt, 97, 102, 10, 15);
    nextInt = constrain(nextInt, 0, 15);
    decValue = (decValue * 16) + nextInt;
  }
  return decValue;
}

int hexToDec2(String hexString) {
  int decValue = 0;
  int nextInt;
  for (int i = 0; i < hexString.length(); i++) {
    nextInt = int(hexString.charAt(i));
    if (nextInt >= 48 && nextInt <= 57) nextInt = map(nextInt, 48, 57, 0, 9);
    if (nextInt >= 65 && nextInt <= 70) nextInt = map(nextInt, 65, 70, 10, 15);
    if (nextInt >= 97 && nextInt <= 102) nextInt = map(nextInt, 97, 102, 10, 15);
    nextInt = constrain(nextInt, 0, 15);
    decValue = (decValue * 16) + nextInt;
  }
  return decValue;
}
