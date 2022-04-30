#include "Leddriver.h"
#include <Arduino.h>

Leddriver::Leddriver() {
    this->ioe = new Ioexpander(LED_ARRAY);
}

void Leddriver::init() {
    this->ioe->init();
    this->ioe->set_conf_reg(0x00);
    this->bits = 0b00000000;
    this->ioe->set_output_reg(this->bits);
}

void Leddriver::on(uint8_t led) {
    this->bits |= 1 << led;
    this->ioe->set_output_reg(this->bits);
}

void Leddriver::off(uint8_t led) {
    this->bits &= ~(1 << led);
    this->ioe->set_output_reg(this->bits);
}