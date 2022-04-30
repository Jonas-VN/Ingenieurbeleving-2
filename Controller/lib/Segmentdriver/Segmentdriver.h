#ifndef Segmentdriver_h
#define Segmentdriver_h

#include "ioexpander.h"
#include <Arduino.h>

#define SEG1 0x3A
#define SEG2 0x39

class Segmentdriver
{
private:
    Ioexpander *ioe;
public:
    Segmentdriver(uint8_t address);

    void init();
    void write_value(char val);
};

#endif