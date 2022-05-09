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
    
  if(strcmp(functionCall,"set_parameters") == 0){
    float _band       = atof(strtok_index);     

    strtok_index      = strtok(NULL, ",");
    float _t_i        = atof(strtok_index);
    
    strtok_index      = strtok(NULL, ",");
    float _t_d        = atof(strtok_index);

    set_parameters(_band, _t_i, _t_d);
  }
  
  if(strcmp(functionCall,"set_direction") == 0){ 
    int dir = atoi(strtok_index);
    motor_direction = (bool) dir;
  }
  
  if(strcmp(functionCall,"set_mode")        == 0){

    if(strcmp(strtok_index,"HOME") == 0){
      set_mode(HOME);
    }   
    else if(strcmp(strtok_index,"SCAN") == 0) {
      set_mode(SCAN);
    }
    else{
      Serial.println("Invaild Mode.");
      return;
    }
  }
  
  if(strcmp(functionCall,"step_motor")      == 0){
    unsigned int number_steps = atoi(strtok_index); 
    for(int i = 0; i < number_steps; i++){
      if( ch)
      step_motor();
    }
  }
  
  if(strcmp(functionCall,"set_setpoint")    == 0){      
    set_setpoint(atof(strtok_index));    
  }
  
  if(strcmp(functionCall,"get_pmt")         == 0){ 
      Serial.println(get_pmt());
  }
  
  if(strcmp(functionCall,"get_mode")        == 0){ 
    MODES _mode = get_mode();
    if(_mode == CLOSED_LOOP){
      Serial.println("CLOSED_LOOP");        
    }
    else{
      Serial.println("OPEN_LOOP");
    }
  }
  
  if(strcmp(functionCall,"get_temperature") == 0){
    float _temperature = get_temperature();
    Serial.println(_temperature,2);
  }
  
  if(strcmp(functionCall,"get_parameters")  == 0){
    Serial.print(band,4);
    Serial.print(',');
    Serial.print(t_integral,4);
    Serial.print(',');
    Serial.println(t_derivative,4);   
  }
  
  if(strcmp(functionCall,"get_setpoint")    == 0){ 
    Serial.println(get_setpoint(),4);    
  }
  
  if(strcmp(functionCall,"get_period")    == 0){ 
    Serial.println(get_period());    
  }

  if(strcmp(functionCall,"get_all_variables") == 0){
    Serial.print(get_temperature(),2);
    Serial.print(',');
    Serial.print(get_setpoint(),4);
    Serial.print(',');
    Serial.print(get_dac());
    Serial.print(',');
    Serial.print(band,4);
    Serial.print(',');
    Serial.print(t_integral,4);
    Serial.print(',');
    Serial.print(t_derivative,4); 
    Serial.print(',');
    Serial.print(get_period());
    Serial.print(','); 
    Serial.print(u1,4); 
    Serial.print(',');
    Serial.print(u2,4); 
    Serial.print(',');
    Serial.println(u3,4); 
  }
}
