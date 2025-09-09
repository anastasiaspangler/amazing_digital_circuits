// Log button presses (single event) + pot changes. Non-blocking LEDs.
#include <Arduino.h>

const uint8_t BTN[4] = {2, 6, 9, 12};
const uint8_t LED[4] = {3, 7, 10, 13};
#define POT_PIN A0

const uint16_t DEBOUNCE_MS = 15;
const uint16_t FLASH_MS    = 1000;
const uint16_t POT_THRESH  = 4;     // only report if change >= 4
const uint16_t POT_MIN_MS  = 25;    // min interval between pot prints

bool lastRead[4]       = {HIGH,HIGH,HIGH,HIGH};
bool stable[4]         = {HIGH,HIGH,HIGH,HIGH};
unsigned long tEdge[4] = {0,0,0,0};
unsigned long ledOffAt[4] = {0,0,0,0};

int lastPot = -1;
unsigned long lastPotPrint = 0;

void setup() {
  for (int i=0;i<4;i++) {
    pinMode(BTN[i], INPUT_PULLUP);  // wire buttons to GND
    pinMode(LED[i], OUTPUT);
    digitalWrite(LED[i], LOW);
  }
  Serial.begin(115200);
}

void loop() {
  unsigned long now = millis();

  // Buttons: debounce, log only on press (LOW edge)
  for (int i=0;i<4;i++) {
    bool r = digitalRead(BTN[i]);
    if (r != lastRead[i]) { lastRead[i] = r; tEdge[i] = now; }
    if ((now - tEdge[i]) >= DEBOUNCE_MS && r != stable[i]) {
      stable[i] = r;
      if (r == LOW) { // pressed
        digitalWrite(LED[i], HIGH);
        ledOffAt[i] = now + FLASH_MS;
        Serial.print("button"); Serial.print(i+1); Serial.println("=1");
      }
    }
  }

  // LEDs: 1 s flash, non-blocking
  for (int i=0;i<4;i++) {
    if (ledOffAt[i] && (long)(now - ledOffAt[i]) >= 0) {
      digitalWrite(LED[i], LOW);
      ledOffAt[i] = 0;
    }
  }

  // Pot: change-only + rate limit
  int pot = analogRead(POT_PIN); // 0..1023
  if ((lastPot < 0) || (abs(pot - lastPot) >= POT_THRESH)) {
    if (now - lastPotPrint >= POT_MIN_MS) {
      Serial.print("pot="); Serial.println(pot);
      lastPot = pot;
      lastPotPrint = now;
    }
  }
}
