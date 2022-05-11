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
  
  if(strcmp(functionCall,"set_direction") == 0){ 
    bool dir = atoi(strtok_index);
    set_direction(dir);
  }
  
  if(strcmp(functionCall,"step_motor") == 0){
    unsigned int number_steps = atoi(strtok_index); 
    
    for(int i = 0; i < number_steps; i++){
      step_motor();
    }
  }
  
  if(strcmp(functionCall,"get_knob") == 0) Serial.println(get_knob());          
  
  if(strcmp(functionCall,"get_pmt") == 0)  Serial.println(get_pmt());

  if(strcmp(functionCall,"get_calibration") == 0){ 
    STATUS _status = get_calibration();
    if     (_status == NOT_DONE)  Serial.println("NOT DONE");        
    else if(_status == FAILED)    Serial.println("FAILED"); 
    else if(_status == COMPLETED) Serial.println("COMPLETED");
    else if(_status == RECAL)     Serial.println("RECALIBRATION");
  }
  
  if(strcmp(functionCall,"get_position")  == 0) Serial.println(get_position());
   
  if(strcmp(functionCall,"get_u1")        == 0) Serial.println(u1);
  
  if(strcmp(functionCall,"get_max_limit") == 0) Serial.println(digitalRead(PIN_SWITCH_MAX)); 
  
  if(strcmp(functionCall,"get_min_limit") == 0) Serial.println(digitalRead(PIN_SWITCH_MIN)); 
  
  if(strcmp(functionCall,"get_direction") == 0) Serial.println(get_direction());   
  
  if(strcmp(functionCall,"home") == 0){
    Serial.println("HOMING");
    home();
  }
  

}
