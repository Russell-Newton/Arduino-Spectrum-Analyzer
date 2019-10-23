#include <FastLED.h>
#include <math.h>

#define NUM_COLUMNS 10
#define COL_HEIGHT 10
#define NUM_LEDS NUM_COLUMNS * COL_HEIGHT
#define DATA_PIN 3
#define MIN_SATURATION 100

CRGB leds[NUM_LEDS];
float hues[NUM_COLUMNS];    //hues assigned to each column, populated in setup

void setup() {
  FastLED.addLeds<WS2812B, DATA_PIN, GRB> (leds, NUM_LEDS);
  Serial.begin(115200);
  for(int i = 0; i < NUM_COLUMNS; i++) {
    hues[i] = 255 / NUM_COLUMNS * (i + 1);
  }
}

void loop() {

}

void setColumnPixels(int column, int height){
  int h = map(height, 0, 255, 0, COL_HEIGHT);
  for(unsigned char y = 0; y < COL_HEIGHT; y++){
    if(y <= h){
      int saturation = map(y, 0, h, MIN_SATURATION, 255);
      leds[y + (column * 10)] = CHSV(hues[column], 255, 255);
    } else {
      leds[y + (column * 10)] = CRGB::Black;
    }
  }
}
