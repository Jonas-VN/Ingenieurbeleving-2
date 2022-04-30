#ifndef Leddriver_h
#define Leddriver_h

#include "ioexpander.h"
#include <Arduino.h>

#define LED_ARRAY 0x3B

#define LED1 7
#define LED2 6
#define LED3 5
#define LED4 4
#define LED5 3

class Leddriver
{
private:
    Ioexpander *ioe;
    uint8_t bits;
public:
    Leddriver();

    void init();
    void on(uint8_t led);
    void off(uint8_t led);    
};

#endif