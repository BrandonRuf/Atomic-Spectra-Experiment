#define sgn(x) ((x) < 0 ? -1 : ((x) > 0 ? 1 : 0)) // Gets the sign (positive or negative) of the argument

unsigned int get_position(){
  return motor_position;
}

byte get_direction(){
  return motor_direction;
}

void set_direction(byte dir){
  motor_direction = dir;
}
