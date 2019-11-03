#include <FastLED.h>
#include <math.h>

#define DATA_PIN 3
#define MIN_SATURATION 150
#define HUE_LOW 100
#define HUE_HIGH 200

CRGB *leds;
float *hues;
int *heights;
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
  heights = new int[NUM_COLUMNS];
  FastLED.addLeds<WS2812B, DATA_PIN, GRB> (leds, NUM_LEDS);
  for(int i = 0; i < NUM_COLUMNS; i++) {
    hues[i] = map(i, 0, NUM_COLUMNS, HUE_LOW, HUE_HIGH);
  }

  // Pong
  delay(100);
  Serial.write((char) CHAR_OFFSET);
  Serial.write((char) (CHAR_OFFSET + NUM_COLUMNS));
  Serial.write((char) (CHAR_OFFSET + COL_HEIGHT));
  Serial.flush();
}

void loop() {
  if(Serial.available() > 0) {
    amassHeights();
    for(int column = 0; column < NUM_COLUMNS; column++) {
      setColumnPixels(column, heights[column]);
//      Serial.write((char) (heights[column] + CHAR_OFFSET + 1));
    }
  }
}

// Set pixels for a given column up to a specific height
void setColumnPixels(int column, int height){
  for(unsigned char y = 0; y < COL_HEIGHT; y++){
    if(y <= height){  // Set up to height
      int saturation = map(height - y, 0, height, MIN_SATURATION, 255);
      leds[y + (column * COL_HEIGHT)] = CHSV(hues[column], 255, 255);
    } else {
      leds[y + (column * COL_HEIGHT)] = CRGB::Black;
    }
  }
  FastLED.show();
}

// Wait for a valid ascii character from serial
char getValidFromSerial() {
  char val = (char) Serial.read();
  while(val < 33) {             // Exclamation point is the first valid character
    val = (char) Serial.read();
  }
  return val;
}

void amassHeights() {
  for(int i = 0; i < NUM_COLUMNS; i++) {
    heights[i] = getValidFromSerial() - CHAR_OFFSET - 1;
  }
}
