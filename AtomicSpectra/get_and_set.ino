#define sgn(x) ((x) < 0 ? -1 : ((x) > 0 ? 1 : 0)) // Gets the sign (positive or negative) of the argument

unsigned int get_pmt(){
  return pmt_voltage;
}

unsigned int get_position(){
  return motor_position;
}

byte get_direction(){
  return motor_direction;
}

MODES get_mode(){
  return mode;
}

void get_knob(){
  /*
   * Get the position of the front pnael knob 
   * on the Monochromator.
   */
  return;
}




void set_direction(byte dir){
  motor_direction = dir;
}

void set_mode(MODES _mode){
    mode = _mode;
} 
