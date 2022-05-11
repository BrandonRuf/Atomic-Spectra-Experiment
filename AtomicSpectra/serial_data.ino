/**
 * Based on "Serial Input Basics" by user Robin2 on Arduino forums.
 * See https://forum.arduino.cc/t/serial-input-basics-updated/382007
 */

const char startMarker = '<';
const char endMarker   = '>'; 

void receive_data() {
  static boolean recv_in_progress = false;
  static byte index = 0;
  char rc;
  
  while (Serial.available() > 0 && newData == false) {
    rc = Serial.read();
   
    if (recv_in_progress == true) {
      
      if (rc != endMarker) {
        received_data[index] = rc;
        index++;
        
        if (index >= data_size) {
          index = data_size - 1;
          // Send warning to user that data buffer is full.
        }
      }
      else {
        received_data[index] = '\0'; // terminate the string
        recv_in_progress = false;
        index = 0;
        newData = true;
        //Serial.println(received_data);
      }
    }

    else if (rc == startMarker) {
        recv_in_progress = true;
    }
  }
}

void parseData() {      
   strtok_index = strtok(temp_data,",");   // Get the first part - the string
   strcpy(functionCall, strtok_index);     // Copy it to function_call
   strtok_index = strtok(NULL, ",");

  if(strcmp(functionCall,"step_motor")    == 0){
    unsigned int number_steps = atoi(strtok_index); 
    
    for(int i = 0; i < number_steps; i++){
      step_motor();
    }
  }

  else if(strcmp(functionCall,"get_pmt")         == 0) Serial.println(get_pmt());
  
  else if(strcmp(functionCall,"set_direction")   == 0) set_direction(atoi(strtok_index));

  else if(strcmp(functionCall,"get_direction")   == 0) Serial.println(get_direction());   

  else if(strcmp(functionCall,"set_control")     == 0){
    if     (strcmp(strtok_index,"FRONT_PANEL") == 0) set_control(FRONT_PANEL);
    else if(strcmp(strtok_index,"COMPUTER")    == 0) set_control(COMPUTER);
  }

  else if(strcmp(functionCall,"get_control")     == 0) Serial.println(CONTROL_MODE_NAMES[get_control()]);
  
  else if(strcmp(functionCall,"get_knob")        == 0) Serial.println(get_knob());          
  
  else if(strcmp(functionCall,"get_calibration") == 0) Serial.println(CALIBRATION_NAMES[get_calibration()]);

  else if(strcmp(functionCall,"get_position")    == 0) Serial.println(get_position());
   
  else if(strcmp(functionCall,"get_u1")          == 0) Serial.println(u1);
  
  else if(strcmp(functionCall,"get_max_limit")   == 0) Serial.println(digitalRead(PIN_SWITCH_MAX)); 
  
  else if(strcmp(functionCall,"get_min_limit")   == 0) Serial.println(digitalRead(PIN_SWITCH_MIN)); 
  
  else if(strcmp(functionCall,"home")            == 0){
    Serial.println("HOMING");
    home();
  }
}
