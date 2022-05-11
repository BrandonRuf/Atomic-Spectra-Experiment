/*
 * For use in the Atomic Spectra experiment in McGill University physics course(s) PHYS-359/439.
 * Written by Brandon Ruffolo in 2022.
 * Based on previous software written by Mark Orchard-Webb (2017) w/ modifications by Katie Savard (2019).
 */
 
#define BAUD 115200              
#define STEP_DELAY 560           // Step delay for motor pulses

#define PIN_STEP 6
#define PIN_DIR  7
#define PIN_SWITCH_MAX 4
#define PIN_SWITCH_MIN 8
#define PIN_KNOB A0
#define PIN_PMT  A1

/** Serial data handling **/
const byte data_size = 64;        // Size of the data buffer receiving from the serial line 
char received_data[data_size];    // Array for storing received data
char temp_data    [data_size];    // Temporary array for use when parsing
char functionCall[20]  = {0};     //
boolean newData = false;          // Flag used to indicate if new data has been found on the serial line
char * strtok_index;              // Used by strtok() as an index

/** Motor control **/
unsigned int motor_position  = 0; // $$(initially 1 to account for arduino reset?)$$
bool         motor_direction = 0;
unsigned int MAX_STEP = 58860;    // 147.15 * (400 microsteps/step) (VERIFIED EMPIRICALLY)
unsigned int MIN_STEP = 100;      // VERIFY THIS

/** Miscellaneous **/ 
unsigned int displacement;
unsigned int sum;
unsigned int u1;
bool _debug = true;

/** Status indicators **/
enum CALIBRATION{NOT_DONE, COMPLETED, FAILED, RECAL};
enum CALIBRATION motor_calibration = NOT_DONE;
const char *CALIBRATION_NAMES[] = {"NOT_DONE","COMPLETED","FAILED","RECAL"};

enum CONTROL_MODE{FRONT_PANEL, COMPUTER};
enum CONTROL_MODE motor_control = FRONT_PANEL;
const char *CONTROL_MODE_NAMES[] = {"FRONT_PANEL","COMPUTER"};

void step_motor(){
  /*
   * 
   */
  digitalWrite(PIN_STEP,1);       // Set step pin high
  delayMicroseconds(STEP_DELAY);  // Delay
  digitalWrite(PIN_STEP,0);       // Set step pin high
  delayMicroseconds(STEP_DELAY);  // Delay 

  if(motor_direction) motor_position--;
  else                motor_position++;
}

void setup() {
  Serial.begin(BAUD);
  pinMode(PIN_STEP,OUTPUT);         // Motor stepping pin
  pinMode(PIN_DIR ,OUTPUT);         // Motor direction pin
  
  pinMode(PIN_SWITCH_MAX, INPUT);   // Max limit switch monitor  
  pinMode(PIN_SWITCH_MIN, INPUT);   // Min limit switch monitor 

  pinMode(LED_BUILTIN, OUTPUT);     // Built-in led for debug purposes

  if(_debug) set_LED(LOW);
}

void loop() {
  receive_data();                       /* Look for and grab data on the serial line. */
                                        /* If new data is found, the newData flag will be set */ 
  if (newData == true) {
      strcpy(temp_data, received_data); /* this temporary copy is necessary to protect the original data    */
                                        /* because strtok() used in parseData() replaces the commas with \0 */
      parseData();                      // Parse the data for commands
      newData = false;                  // Reset newData flag
  }
}

void home(){
  if(_debug) set_LED(HIGH);
  
  motor_position = 0;                 // Reset motor position variable
  set_direction(LOW);                 // Set to increasing motor direction

  /* Step the motor and count steps until hitting the switch */
  while(1){ 
      if( check_bounds() ){
        set_calibration(FAILED);     // Record homing failure
        break;                       // Exit
      } 
      if( check_max_limit() ) break; // Exit if switch was triggered 
      step_motor();                  // Step the motor
  }
  set_direction(HIGH);               // Reverse direction
  displacement = motor_position;     // Save total displacement to the limit switch
  motor_position = MAX_STEP;         // Set the motor position to its (now) known location         
    
  /* Bring the motor back to its original position */
  while(displacement){
    step_motor();                    
    displacement--;
  }

  if(get_calibration() != FAILED) set_calibration(COMPLETED); // Update motor calibration status
  if(_debug) set_LED(LOW);
}
