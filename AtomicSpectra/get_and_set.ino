unsigned int get_pmt(){
  /*
   * Get PMT voltage.
   * Returns a 10-bit number (0-1023).
   */
  return analogRead(PIN_PMT);
}

unsigned int get_position(){
  /*
   * Get absolute motor position. 
   */
  return motor_position;
}

bool get_direction(){
  /*
   * Get motor direction. LOW and HIGH 
   * are the forward and reverse directions, respectively.
   */
  return motor_direction;
}

unsigned int get_knob(){
  /*
   * Get the position of the front panel knob 
   * on the Monochromator.
   */
   return analogRead(PIN_KNOB);
}

CALIBRATION get_calibration(){
  /*
   * Get the current calibration of the motor.
   */
  return motor_calibration;
}


void set_calibration(CALIBRATION _status){
  /*
   * Set the calibration of the motor.
   */
  motor_calibration = _status;
}

void set_direction(bool dir){
  /*
   * Set direction of the motor.
   * LOW and HIGH are the forward and reverse 
   * directions, respectively.
   */
  digitalWrite(PIN_DIR,dir);     
  motor_direction = dir;         
}

void set_LED(bool _power){
  /*
   * Set the state of the built-in led on the 
   * arduino board (connected to pin 13).
   */
  digitalWrite(LED_BUILTIN, _power);
}


bool check_bounds(){
  /*
   * MODDED FOR DEBUG!!!!
   * Check if motor has exceeded position limits,
   * as defined in software by the macros MAX_STEP, MIN_STEP. 
   */
   if (motor_position > MAX_STEP/10) return true;
   else return false;
}

bool check_max_limit(){
   /*
   * Check if motor has hit the forward 
   * limit switch on the hardware. 
   */
   return digitalRead(PIN_SWITCH_MAX);
}
