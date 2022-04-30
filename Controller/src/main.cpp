#include <Arduino.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_VEML7700.h>
#include "Segmentdriver.h"
#include "Leddriver.h"

#define BUTTON_LED1 6
#define BUTTON1 14
#define BUTTON_LED2 39
#define BUTTON2 15
#define BUTTON_LED3 8
#define BUTTON3 16
#define BUTTON_LED4 9
#define BUTTON4 17
#define BUTTON_LED5 10
#define BUTTON5 18
#define SPRINT 24
#define BUZZER 2
#define VIBRATOR1 12
#define VIBRATOR2 5

int buzzerCount = 0;
int vibratorCount = 0;
int readScore = 0;

boolean paused = false;
boolean buzzer = false;
boolean vibrator = false;
boolean gameOver = false;

Segmentdriver Seg1(SEG1);
Segmentdriver Seg2(SEG2);
Leddriver Leds;
Adafruit_MPU6050 mpu;
Adafruit_VEML7700 veml;

// Reset the leds and 7-segment displays
void resetAll() {
  Leds.off(LED1);
  Leds.off(LED2);
  Leds.off(LED3);
  Leds.off(LED4);
  Leds.off(LED5);
  digitalWrite(BUTTON_LED1, LOW);
  digitalWrite(BUTTON_LED2, LOW);
  digitalWrite(BUTTON_LED3, LOW);
  digitalWrite(BUTTON_LED4, LOW);
  digitalWrite(BUTTON_LED5, LOW);
  digitalWrite(VIBRATOR1, LOW);
  digitalWrite(VIBRATOR2, LOW);
  noTone(BUZZER);
  Seg1.write_value(' '); 
  Seg2.write_value(' ');
}

// Coffin dance to play on the buzzer when the game is over
void CoffinDance() {
  int NOTE_F4 = 349, NOTE_G4 = 392, NOTE_A4 = 440, NOTE_AS4 = 466, NOTE_C5 = 523, NOTE_D5 = 587, NOTE_G5 = 784, NOTE_A5 = 880, NOTE_AS5 = 932;
  int melody[] = { NOTE_G5, NOTE_G5, NOTE_G5, NOTE_G5, NOTE_G5, NOTE_G5, NOTE_C5, NOTE_AS4, NOTE_A4, NOTE_F4, NOTE_G4, 0, NOTE_G4, NOTE_D5, NOTE_C5, 0, NOTE_AS4, 0, NOTE_A4, 0, NOTE_A4, NOTE_A4, NOTE_C5, 0, NOTE_AS4, NOTE_A4, NOTE_G4,0, NOTE_G4, NOTE_AS5, NOTE_A5, NOTE_AS5, NOTE_A5, NOTE_AS5, NOTE_G4,0, NOTE_G4, NOTE_AS5, NOTE_A5, NOTE_AS5, NOTE_A5, NOTE_AS5};

    for (int thisNote = 0; thisNote < 42; thisNote++) {
      if (melody[thisNote] <= NOTE_G4 || melody[thisNote] >= NOTE_AS5) {Leds.on(LED1); Leds.on(LED2); Leds.on(LED3); Leds.on(LED4); Leds.on(LED5); digitalWrite(BUTTON_LED1, 1), digitalWrite(BUTTON_LED2, 1) ,digitalWrite(BUTTON_LED3, 1), digitalWrite(BUTTON_LED4, 1), digitalWrite(BUTTON_LED5, 1); Seg1.write_value('8'); Seg2.write_value('8');}
      int noteDuration = 750 / 4;
      tone(BUZZER, melody[thisNote] / 2, noteDuration);  // /2 zelf toegevoegd
      int pauseBetweenNotes = noteDuration * 1.30;
      delay(pauseBetweenNotes);
      noTone(BUZZER);
      resetAll();
    }
}

// Handles everything for the movementbuttons
void movementButton(int BUTTON, int BUTTUN_LED, char richting) {
  if (digitalRead(BUTTON) != HIGH) {
    digitalWrite(BUTTUN_LED, HIGH);
    SerialUSB.print(richting);
  }
  else {
    digitalWrite(BUTTUN_LED, LOW);
  }
}

// Gets the data from the PC and handles it
void getDataFromPC() {    
  while(SerialUSB.available() > 0) {
    char x = SerialUSB.read();

    // Handle all the input from PC to display on the arduino
    switch (x) {
      case 'm': paused = true; break;
      case 'u': paused = false; break;
      case 'b': buzzer = true; break;
      case 'v': vibrator = true; break;
      case 'o': Leds.on(LED1); break;
      case 'c': Leds.on(LED2); break;
      case 'n': Leds.on(LED3); break;
      case 'e': Leds.on(LED4); break;
      case 'f': Leds.on(LED5); break;
      case 'h': Leds.off(LED1); break;
      case 'i': Leds.off(LED2); break;
      case 'j': Leds.off(LED3); break;
      case 'k': Leds.off(LED4); break;
      case 'l': Leds.off(LED5); break;
      case 'g': gameOver = true; CoffinDance(); buzzer = false; vibrator = false; resetAll(); break;
    }
    
    // Read score from PC
    if (x == ')') readScore = 0;
    else if (readScore == 2) {
      Seg2.write_value(x);
    }
    else if (readScore == 1) {
      Seg1.write_value(x);
      readScore = 2;
    }
    else if (x == '(') readScore = 1;
  }
};


void setup() {
  // Start serial communication and wait until the Arduino is ready
  SerialUSB.begin(1000000);
  while (!SerialUSB) {}

  // Init libraries
  veml.begin();
  mpu.begin();
  Leds.init();
  Seg1.init();
  Seg2.init();

  // Buttons and leds init
  pinMode(BUTTON_LED1, OUTPUT);
  pinMode(BUTTON1, INPUT);
  pinMode(BUTTON_LED2, OUTPUT);
  pinMode(BUTTON2, INPUT);
  pinMode(BUTTON_LED3, OUTPUT);
  pinMode(BUTTON3, INPUT);
  pinMode(BUTTON_LED4, OUTPUT);
  pinMode(BUTTON4, INPUT);
  pinMode(BUTTON_LED5, OUTPUT);
  pinMode(BUTTON5, INPUT);
  pinMode(SPRINT, INPUT);

  // Reset every button/led
  resetAll();
};


void loop() {
  // Empty loop to sync with game
  while (SerialUSB.readStringUntil('!') != "w" && !gameOver) {}

  // Get data from PC/game
  getDataFromPC();

  // Get data from IMU and send to PC
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);
  SerialUSB.print("[");
  SerialUSB.print(asinf(a.acceleration.x / 100) * RAD_TO_DEG); // pitch
  SerialUSB.print("/");
  SerialUSB.print(atan2f(a.acceleration.y, a.acceleration.z) * RAD_TO_DEG / 100); // roll
  SerialUSB.print("]");

  // Get data from VEML and send to PC
  SerialUSB.print("{");
  SerialUSB.print(veml.readLux());
  SerialUSB.print("}");

  // Movementbuttons to PC
  movementButton(BUTTON1, BUTTON_LED1, 'z');
  movementButton(BUTTON2, BUTTON_LED2, 'd');
  movementButton(BUTTON3, BUTTON_LED3, 's');
  if (paused && !digitalRead(BUTTON3)) delay(250); // delay 250 ms to prevent double press on pause (debounce)
  movementButton(BUTTON4, BUTTON_LED4, 'q');

  // Sprint button to PC
  if (digitalRead(SPRINT) == HIGH) SerialUSB.print("a");

  // Pause button to PC and light up led
  if (digitalRead(BUTTON5) != HIGH) SerialUSB.print("p");
  if (paused) digitalWrite(BUTTON_LED5, HIGH);
  else digitalWrite(BUTTON_LED5, LOW);

  // Buzzer
  if (buzzer && buzzerCount <= 15) {
    tone(BUZZER, 450);
    buzzerCount++;
  }
  else {
    noTone(BUZZER);
    buzzerCount = 0;
    buzzer = false;
  }
  
  // Vibrator
  if (vibrator && vibratorCount <= 15) {
    digitalWrite(VIBRATOR1, HIGH);
    digitalWrite(VIBRATOR2, HIGH);
    vibratorCount++;
  }
  else {
    digitalWrite(VIBRATOR1, LOW);
    digitalWrite(VIBRATOR2, LOW);
    vibratorCount = 0;
    vibrator = false;
  }
};