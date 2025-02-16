#include <SerialTransfer.h>

SerialTransfer xfer;

const byte pins[4][3] = {
  {2, 3, 4},   // North: R, Y, G
  {5, 6, 7},   // South
  {8, 9, 10},  // East
  {11, 12, 13} // West
};

struct {
  uint16_t north;
  uint16_t south;
  uint16_t east;
  uint16_t west;
} counts;

void setLight(byte direction, byte state) {
  digitalWrite(pins[direction][0], state & 0b100 ? HIGH : LOW);
  digitalWrite(pins[direction][1], state & 0b010 ? HIGH : LOW);
  digitalWrite(pins[direction][2], state & 0b001 ? HIGH : LOW);
}

void transitionLights(byte activeDir) {
  for(byte i=0; i<4; i++){
    if(i == activeDir) {
      setLight(i, 0b001);  // Green
    } else {
      setLight(i, 0b100);  // Red
    }
  }
}

void setup() {
  Serial.begin(115200);
  xfer.begin(Serial);
  
  for(byte i=0; i<12; i++){
    pinMode(2+i, OUTPUT);
    digitalWrite(2+i, LOW);
  }
}

void loop() {
  if(xfer.available()) {
    xfer.rxObj(counts);
    
    uint16_t maxCount = max(max(counts.north, counts.south), 
                           max(counts.east, counts.west));
                           
    if(maxCount > 8) {  // Congestion threshold
      if(counts.north == maxCount) transitionLights(0);
      else if(counts.south == maxCount) transitionLights(1);
      else if(counts.east == maxCount) transitionLights(2);
      else transitionLights(3);
      
      delay(1000 * (10 + min(maxCount, 20)));  // 10-30s green
    } else {
      // Rotate green lights every 15s
      static byte currentDir = 0;
      transitionLights(currentDir);
      currentDir = (currentDir + 1) % 4;
      delay(15000);
    }
  }
}
