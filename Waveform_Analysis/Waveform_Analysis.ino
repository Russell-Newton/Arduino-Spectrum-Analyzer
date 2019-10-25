#include <FastLED.h>
#include <math.h>

#define DATA_PIN 3
#define MIN_SATURATION 150

CRGB *leds;
float *hues;
int CHAR_OFFSET = -1;
int NUM_COLUMNS = -1;
int COL_HEIGHT = -1;
int NUM_LEDS = -1;
bool initialized = false;

void setup() {
  Serial.begin(115200);
  
  Serial.print("!");  // Send hello
  while(!initialized) { // They don't have to be sent as one string, but it will definitely work if they are
    if(Serial.available() > 0) {
      CHAR_OFFSET = getValidFromSerial(); // This is used to get normal numbers from the characters sent over serial

      // Setup matrix dimensions
      NUM_COLUMNS = getValidFromSerial() - CHAR_OFFSET;
      COL_HEIGHT = getValidFromSerial() - CHAR_OFFSET;
      NUM_LEDS = NUM_COLUMNS * COL_HEIGHT;

      // Break
      initialized = true;
    }
  }

  // Setup matrix
  leds = new CRGB[NUM_LEDS];
  hues = new float[NUM_COLUMNS];
  FastLED.addLeds<WS2812B, DATA_PIN, GRB> (leds, NUM_LEDS);
  for(int i = 0; i < NUM_COLUMNS; i++) {
    hues[i] = 255 / NUM_COLUMNS * (i + 1);
  }
  delay(100);
  Serial.write((char) CHAR_OFFSET);
  Serial.write((char) (CHAR_OFFSET + NUM_COLUMNS));
  Serial.write((char) (CHAR_OFFSET + COL_HEIGHT));
  Serial.flush();
}

void loop() {
  if(Serial.available() > 0) {
    Serial.write((char) Serial.read());
  }
}

// Set pixels for a given column up to a specific height
void setColumnPixels(int column, int height){
  for(unsigned char y = 0; y < COL_HEIGHT; y++){
    if(y <= height){  // Set up to height
      int saturation = map(height - y, 0, height, MIN_SATURATION, 255);
      leds[y + (column * 10)] = CHSV(hues[column], 255, 255);
    } else {
      leds[y + (column * 10)] = CRGB::Black;
    }
  }
  FastLED.show();
}

// Wait for a valid ascii character from serial
char getValidFromSerial() {
  char val = (char) Serial.read();
  while(val < 33) {
    val = (char) Serial.read();
  }
  return val;
}
