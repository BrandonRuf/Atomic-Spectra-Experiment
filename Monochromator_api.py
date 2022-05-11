import serial as _serial
import time   as _time


_serial_left_marker  = '<'
_serial_right_marker = '>'  

_debug_enabled       = True 

CONTROL_MODES = ["FRONT_PANEL", "COMPUTER"]

class Monochromator_api():
    """
    Commands-only object for interacting with the arduino based
    Atomic Spectra Monochromator hardware.
    
    Parameters
    ----------
    port='COM4' : str
        Name of the port to connect to.
    baudrate=115200 : int
        Baud rate of the connection. Must match the instrument setting.
    timeout=15 : number
        How long to wait for responses before giving up (s). 
        
    """
    def __init__(self, port='COM4', address=0, baudrate=115200, timeout=3):
                
        if not _serial:
            print('You need to install pyserial to use the Atomic Spectra Monochromator.')
            self.simulation_mode = True
        
        self.simulation_mode = False
        
        # If the port is "Simulation"
        if port=='Simulation': self.simulation_mode = True
        
        # If we have all the libraries, try connecting.
        if not self.simulation_mode:
            try:
                # Create the instrument and ensure the settings are correct.
                self.serial = _serial.Serial(port = port, baudrate = baudrate, timeout = timeout)
                
            # Something went wrong. Go into simulation mode.
            except Exception as e:
                  print('Could not open connection to "'+port+':'+'" at baudrate '+str(baudrate)+'. Entering simulation mode.')
                  print(e)
                  self.simulation_mode = True
                  self.serial = None
        
        # Give the arduino time to run the setup loop
        _time.sleep(2)
        
    
    def set_control(self,mode):
        """
        Set the control mode of the of the monochromator motor.
        
        Parameters
        ----------
        mode : str
            The desired operating mode.

        """
        
        if mode not in CONTROL_MODES:
            print("Controller mode has not been changed. %s is not a vaild mode."%mode)
            return 
        
        if self.simulation_mode: 
            return
        
        self.write("set_control,%s"%mode)
        
    def get_control(self):
        """
        Get the control mode of the of the monochromator motor.
        
        Returns
        ----------
        mode : str
            The current operating mode.

        """
        
        self.write("get_control")
        
        return self.read()
        
    def set_direction(self, direction):
        """
        Set the direction of the motor.
        
        Parameters
        ----------
        direction: bool
            False and True are the forward and backward directions, respectively.
            
        """
        self.write("set_direction,%d"%direction)
        
    def get_calibration(self):
        """
        Get the current status of operation.
        
        """
        self.write('get_calibration')
        
        return self.read()
    
    def get_direction(self):
        """
        Get the current motor direction.

        Returns
        -------
        direction: bool
            False and True are the forward and backward directions, respectively.

        """
        self.write("get_direction")
        
        return bool(self.read())        
        
    def get_position(self):
        """
        Get the current absolute position of the Monochromator motor.

        """
        if self.simulation:
            return
        
        self.write('get_position')
        
        return int(self.read())
    
    def get_pmt(self):
        """
        Get the photomultiplier tube (PMT) something.

        Returns
        -------
        int
            Digitized voltage [0-2**(bit_depth)-1].

        """
        
        self.write("get_pmt")
        
        return int(self.read())
    
    def home(self):
        """
        Home the motor.
        """
        self.write('home')
        
        if self.read() == "HOMING": return True
        else                      : return False
        
        
    def write(self,raw_data):
        """
        Writes data to the serial line, formatted appropriately to be read by the monochromator.        
        
        Parameters
        ----------
        raw_data : str
            Raw data string to be sent to the arduino.
        
        Returns
        -------
        None.
        
        """
        encoded_data = (_serial_left_marker + raw_data + _serial_right_marker).encode()
        self.serial.write(encoded_data) 
    
    def read(self):
        """
        Reads data from the serial line.
        
        Returns
        -------
        str
            Raw data string read from the serial line.
        """
        return self.serial.read_until(expected = '\r\n'.encode()).decode().strip('\r\n')
            
    def disconnect(self):
        """
        Disconnects the port.
        """
        if not self.simulation_mode and self.serial != None: 
            self.serial.close()
            self.serial = None
