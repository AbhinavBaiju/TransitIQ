#include <SerialTransfer.h>

SerialTransfer xfer;

const byte pins[4][3] = {
  {8, 9, 10},   // North: R, Y, G
  {5, 6, 7},   // South
  {2, 3, 4},  // East
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
  // First, set yellow for the previously active direction and red for others
  for(byte i=0; i<4; i++){
    if(i == (activeDir == 0 ? 3 : activeDir - 1)) {
      setLight(i, 0b010);  // Yellow
    } else {
      setLight(i, 0b100);  // Red
    }
  }
  
  // Wait for 1 second during yellow phase
  delay(1000);
  
  // Then transition to the new active direction
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
    
    // Store car counts in array for easier iteration
    uint16_t carCounts[] = {counts.north, counts.south, counts.east, counts.west};
    static byte currentDir = 0;
    
    // Find next direction with cars
    byte nextDir = currentDir;
    bool foundNextDir = false;
    
    // Try up to 4 times to find a direction with cars
    for(byte i = 0; i < 4; i++) {
      nextDir = (currentDir + i) % 4;
      if(carCounts[nextDir] > 0) {
        foundNextDir = true;
        break;
      }
    }
    
    // If we found a direction with cars, transition to it
    if(foundNextDir) {
      transitionLights(nextDir);
      // Calculate green light duration: 4 seconds per car
      uint32_t greenDuration = carCounts[nextDir] * 4000UL;
      delay(greenDuration);
      currentDir = (nextDir + 1) % 4;
    } else {
      // If no cars anywhere, just rotate every 5 seconds
      transitionLights(currentDir);
      delay(5000);
      currentDir = (currentDir + 1) % 4;
    }
    
    // Send ready signal back to Python
    xfer.txObj(true);
  }
}