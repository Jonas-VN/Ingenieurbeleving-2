#include "Segmentdriver.h"
#include <Arduino.h>

Segmentdriver::Segmentdriver(uint8_t address) {
    this->ioe = new Ioexpander(address);
}

void Segmentdriver::init() {
    this->ioe->init();
    this->ioe->set_conf_reg(0x00);
    this->write_value('0');
}

void Segmentdriver::write_value(char val) {
    switch (val) {
        case '0': ioe->set_output_reg(0b11000000); break;
        case '1': ioe->set_output_reg(0b11111001); break;
        case '2': ioe->set_output_reg(0b10100100); break;
        case '3': ioe->set_output_reg(0b10110000); break;
        case '4': ioe->set_output_reg(0b10011001); break;
        case '5': ioe->set_output_reg(0b10010010); break;
        case '6': ioe->set_output_reg(0b10000010); break;
        case '7': ioe->set_output_reg(0b11111000); break;
        case '8': ioe->set_output_reg(0b10000000); break;
        case '9': ioe->set_output_reg(0b10010000); break;
        case 'A': ioe->set_output_reg(0b10001000); break;
        case 'a': ioe->set_output_reg(0b10100000); break;
        case 'b': ioe->set_output_reg(0b10000011); break;
        case 'C': ioe->set_output_reg(0b11000110); break;
        case 'c': ioe->set_output_reg(0b10100111); break;
        case 'd': ioe->set_output_reg(0b10100001); break;
        case 'E': ioe->set_output_reg(0b10000110); break;
        case 'F': ioe->set_output_reg(0b10001110); break;
        case 'G': ioe->set_output_reg(0b11000010); break;
        case 'H': ioe->set_output_reg(0b10001001); break;
        case 'h': ioe->set_output_reg(0b10001011); break;
        case 'I': ioe->set_output_reg(0b11001111); break;
        case 'J': ioe->set_output_reg(0b11100001); break;
        case 'L': ioe->set_output_reg(0b11000111); break;
        case 'n': ioe->set_output_reg(0b10101011); break;
        case 'O': ioe->set_output_reg(0b11000000); break;
        case 'o': ioe->set_output_reg(0b10100011); break;
        case 'P': ioe->set_output_reg(0b10001100); break;
        case 'q': ioe->set_output_reg(0b10011000); break;
        case 'r': ioe->set_output_reg(0b10101111); break;
        case 'S': ioe->set_output_reg(0b10010010); break;
        case 't': ioe->set_output_reg(0b10000111); break;
        case 'U': ioe->set_output_reg(0b11000001); break;
        case 'u': ioe->set_output_reg(0b11100011); break;
        case 'y': ioe->set_output_reg(0b10010001); break;
        case ' ': ioe->set_output_reg(0b11111111); break;

    default: ioe->set_output_reg(0b11111111); break;
    }
}