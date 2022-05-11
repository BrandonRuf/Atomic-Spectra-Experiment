import spinmob.egg   as _egg
import spinmob       as _s
import os            as _os
import serial        as _serial

import time     as _time
import shutil   as _shutil
import numpy    as _n
import scipy.special as _scipy_special
import sys as _sys

import traceback as _traceback
_p = _traceback.print_last
_d = _s.data

# import pyqtgraph and create the App.
import pyqtgraph as _pg
from spinmob.egg._gui import Button, ComboBox, NumberBox, Label, TextBox
_g = _egg.gui

from serial.tools.list_ports import comports as _comports
from Monochromator_api    import Monochromator_api

# GUI settings
_s.settings['dark_theme_qt'] = True

# Defined fonts
style_1 = 'font-size: 14pt; font-weight: bold; color: '+('mediumspringgreen' if _s.settings['dark_theme_qt'] else 'blue')
style_2 = 'font-size: 17pt; font-weight: bold; color: '+('white'             if _s.settings['dark_theme_qt'] else 'red')
style_3 = 'font-size: 17pt; font-weight: bold; color: '+('cyan'              if _s.settings['dark_theme_qt'] else 'purple')



class serial_gui_base(_g.BaseObject):
    """
    Base class for creating a serial connection gui. Handles common controls.
    
    Parameters
    ----------
    api_class=None : class
        Class to use when connecting. For example, api_class=PCIT1_api would
        work. Note this is not an instance, but the class itself. An instance is
        created when you connect and stored in self.api.
        
    name='serial_gui' : str
        Unique name to give this instance, so that its settings will not
        collide with other egg objects.
        
    show=True : bool
        Whether to show the window after creating.
        
    block=False : bool
        Whether to block the console when showing the window.
        
    window_size=[1,1] : list
        Dimensions of the window.
    hide_address=False: bool
        Whether to show the address control for things like the Auber.
    """
    def __init__(self, api_class = None, name='serial_gui', show=True, block=False, window_size=[1,1], hide_address=False):

        # Remebmer the name.
        self.name = name

        # Checks periodically for the last exception
        self.timer_exceptions = _g.TimerExceptions()
        self.timer_exceptions.signal_new_exception.connect(self._new_exception)

        # Where the actual api will live after we connect.
        self.api = None
        self._api_class = api_class

        # GUI stuff
        self.window   = _g.Window(
            self.name, size=window_size, autosettings_path=name+'.window',
            event_close = self._window_close)
        
        # Top of GUI (Serial Communications)
        self.grid_top = self.window.place_object(_g.GridLayout(margins=False), alignment=0)
        self.window.new_autorow()

        # Get all the available ports
        self._label_port = self.grid_top.add(_g.Label('Port:'))
        self._ports = [] # Actual port names for connecting
        ports       = [] # Pretty port names for combo box
        if _comports:
            for p in _comports():
                self._ports.append(p.device)
                ports      .append(p.description)
        
        # Append simulation port
        ports      .append('Simulation')
        self._ports.append('Simulation')
        
        # Append refresh port
        ports      .append('Refresh - Update Ports List')
        self._ports.append('Refresh - Update Ports List')
        
        self.combo_ports = self.grid_top.add(_g.ComboBox(ports, autosettings_path=name+'.combo_ports'))
        self.combo_ports.signal_changed.connect(self._ports_changed)
        

        self.grid_top.add(_g.Label('Address:')).show(hide_address)
        self.number_address = self.grid_top.add(_g.NumberBox(
            0, 1, int=True,
            autosettings_path=name+'.number_address',
            tip='Address (not used for every instrument)')).set_width(40).show(hide_address)

        self.grid_top.add(_g.Label('Baud:'))
        self.combo_baudrates = self.grid_top.add(_g.ComboBox(
            ['9600','57600', '115200','230400'],
            default_index=2,
            autosettings_path=name+'.combo_baudrates'))

        self.grid_top.add(_g.Label('Timeout:'))
        self.number_timeout = self.grid_top.add(_g.NumberBox(.05, dec=True, bounds=(.01, None), suffix='s', tip='How long to wait for an answer before giving up (ms).', autosettings_path=name+'.number_timeout')).set_width(100)

        # Button to connect
        self.button_connect  = self.grid_top.add(_g.Button('Connect', checkable=True))

        # Stretch remaining space
        self.grid_top.set_column_stretch(self.grid_top._auto_column)

        # Connect signals
        self.button_connect.signal_toggled.connect(self._button_connect_toggled)
        
        # Status
        self.label_status = self.grid_top.add(_g.Label(''))
        
        # Error
        self.grid_top.new_autorow()
        self.label_message = self.grid_top.add(_g.Label(''), column_span=10).set_colors('pink' if _s.settings['dark_theme_qt'] else 'red')

        # Other data
        self.t0 = None

        # Run the base object stuff and autoload settings
        _g.BaseObject.__init__(self, autosettings_path=name)

        # Show the window.
        if show: self.window.show(block)
    
    def _ports_changed(self):
        """
        Refreshes the list of availible serial ports in the GUI.

        """
        if self.get_selected_port() == 'Refresh - Update Ports List':
            
            len_ports = len(self.combo_ports.get_all_items())
            
            # Clear existing ports
            if(len_ports > 1): # Stop recursion!
                for n in range(len_ports):
                    self.combo_ports.remove_item(0)
            else:
                return
                self.combo_ports.remove_item(0)
                 
            self._ports = [] # Actual port names for connecting
            ports       = [] # Pretty port names for combo box
                
            default_port = 0
             
            # Get all the available ports
            if _comports:
                for inx, p in enumerate(_comports()):
                    self._ports.append(p.device)
                    ports      .append(p.description)
                    
                    if 'Arduino' in p.description:
                        default_port = inx
                        
            # Append simulation port
            ports      .append('Simulation')
            self._ports.append('Simulation')
            
            # Append refresh port
            ports      .append('Refresh - Update Ports List')
            self._ports.append('Refresh - Update Ports List')
             
            # Add the new list of ports
            for item in ports:
                self.combo_ports.add_item(item)
             
            # Set the new default port
            self.combo_ports.set_index(default_port)
    
    def _button_connect_toggled(self, *a):
        """
        Connect by creating the API.
        """
        if self._api_class is None:
            raise Exception('You need to specify an api_class when creating a serial GUI object.')

        # If we checked it, open the connection and start the timer.
        if self.button_connect.is_checked():
            port = self.get_selected_port()
            self.api = self._api_class(
                    port=port,
                    baudrate=int(self.combo_baudrates.get_text()),
                    timeout=self.number_timeout.get_value())

            # Record the time if it's not already there.
            if self.t0 is None: self.t0 = _time.time()

            # Enable the grid
            self.grid_bot.enable()

            # Disable serial controls
            self.combo_baudrates.disable()
            self.combo_ports    .disable()
            self.number_timeout .disable()
            
            
            if self.api.simulation_mode:
                #self.label_status.set_text('*** Simulation Mode ***')
                #self.label_status.set_colors('pink' if _s.settings['dark_theme_qt'] else 'red')
                self.combo_ports.set_value(len(self._ports)-2)
                self.button_connect.set_text("Simulation").set_colors(background='pink')
            else:
                self.button_connect.set_text('Disconnect').set_colors(background = 'blue')

        # Otherwise, shut it down
        else:
            self.api.disconnect()
            #self.label_status.set_text('')
            self.button_connect.set_colors()
            self.grid_bot.disable()

            # Enable serial controls
            self.combo_baudrates.enable()
            self.combo_ports    .enable()
            self.number_timeout .enable()
            
            self.button_connect.set_text('Connect').set_colors(background = '')


        # User function
        self._after_button_connect_toggled()

    def _after_button_connect_toggled(self):
        """
        Dummy function called after connecting.
        """
        return

    def _new_exception(self, a):
        """
        Just updates the status with the exception.
        """
        self.label_message(str(a)).set_colors('red')

    def _window_close(self):
        """
        Disconnects. When you close the window.
        """
        print('Window closed but not destroyed. Use show() to bring it back.')
        if self.button_connect():
            print('  Disconnecting...')
            self.button_connect(False)

    def get_selected_port(self):
        """
        Returns the actual port string from the combo box.
        """
        return self._ports[self.combo_ports.get_index()]
    
    def get_com_ports():
        """
        Returns a dictionary of port names as keys and descriptive names as values.
        """
        if _comports:
    
            ports = dict()
            for p in _comports(): ports[p.device] = p.description
            return ports
    
        else:
            raise Exception('You need to install pyserial and have Windows to use get_com_ports().')
            
    def list_com_ports():
        """
        Prints a "nice" list of available COM ports.
        """
        ports = get_com_ports()
    
        # Empty dictionary is skipped.
        if ports:
            keys = list(ports.keys())
            keys.sort()
            print('Available Ports:')
            for key in keys:
                print(' ', key, ':', ports[key])
    
        else: raise Exception('No ports available. :(')
        
        

class Monochrmator(serial_gui_base):

    def __init__(self, name='Monochromator', api = Monochromator_api, show=True, block=False, window_size=[1,300]):


        # Run the base class stuff, which shows the window at the end.
        serial_gui_base.__init__(self, api_class=api, name=name, show=False, window_size=window_size)
        
        self.window.set_size([0,0])
        
        # Build the GUI
        self.gui_components(name)
        
        # Finally show it.
        self.window.show(block)
        
    def _after_button_connect_toggled(self):
        """
        Called after the connection or disconnection routine.
    
        """

        
        if self.button_connect.is_checked():
    
            # Get the setpoint
            try:
                
                self._update_status("Homing")
                
                
                
                self.grid_bot.enable()
                                
                self.timer.start()
                
                self.api.home()
                
                
            except:
                self.button_connect.set_checked(False)
        
        # Disconnected
        else:
            self.grid_bot.disable()
            self.timer.stop()
    
    def _update_status(self, status = None):
        if status == None:
            self.textbox_status.set_text(self.api.get_calibration())
        else:
            self.textbox_status.set_text(status)
        
    
    def _timer_tick(self, *a):
        """
        Called whenever the timer ticks. Let's update the plot and save the latest data.
        """
        current_time = _time.time()
        
        self.api.serial.reset_input_buffer()
        status = self.api.get_calibration()
        

        if status == '': status = "Homing"
        
        self._update_status(status)
            
        
        # Get the time, temperature, and setpoint
        t = current_time - self.t0
        '''
        self.plot.append_row([t, t**2], ckeys=['Time (s)', 'Counts (C)'])
        self.plot.plot()
        '''
        
        # Update the GUI
        self.window.process_events()
    
    def gui_components(self,name):
        
        self.grid_upper_mid = self.window.place_object(_g.GridLayout(margins=False), alignment = 1)
        

        
        
        self.grid_upper_mid.add(_g.Label('Status:'), alignment=1, row_span=1).set_style(style_2)
        
        self.textbox_status = self.grid_upper_mid.add(_g.TextBox(
            "--", tip='A test.'),
            alignment=1).set_width(150).disable().set_style(style_2)
        
        self.grid_upper_mid.new_autorow()
        self.grid_upper_mid.add(_g.Label('Position:'), alignment=2, row_span=1).set_style('font-size: 14pt; font-weight: bold; color: cyan')
        self.numberbox_position = self.grid_upper_mid.add(_g.NumberBox(0, tip='A test.'),
            alignment=2).set_width(125).disable().set_style('font-size: 14pt; font-weight: bold; color: cyan')
        
        self.grid_upper_mid.add(_g.Label('Calibration:'), alignment=2, row_span=1).set_style('font-size: 14pt; font-weight: bold; color: cyan')
        self.textbox_calibration = self.grid_upper_mid.add(_g.Button(text='Completed'),
            alignment=2).set_width(150).disable().set_style('font-size: 14pt; font-weight: bold;').set_colors(text = "limegreen",background='white')
        
        self.grid_upper_mid.add(_g.Label('Max Limit:'), alignment=2, row_span=1).set_style('font-size: 14pt; font-weight: bold; color: cyan')
        self.numberbox_min = self.grid_upper_mid.add(_g.Button(text=""),
            alignment=2).set_width(20).disable().set_colors(background='limegreen')
        
        self.grid_upper_mid.new_autorow()
        self.grid_upper_mid.add(_g.Label('Speed:'), alignment=2, row_span=1).set_style('font-size: 14pt; font-weight: bold; color: cyan')
        self.numberbox_speed = self.grid_upper_mid.add(_g.NumberBox(0, tip='A test.'),
            alignment=2).set_width(125).disable().set_style('font-size: 14pt; font-weight: bold; color: cyan')
        
        self.grid_upper_mid.add(_g.Label('Control:'), alignment=2, row_span=1).set_style('font-size: 14pt; font-weight: bold; color: cyan')
        self.textbox_control = self.grid_upper_mid.add(_g.Button(text='Front Panel'),
            alignment=2).set_width(150).disable().set_style('font-size: 14pt; font-weight: bold;').set_colors(text = "white",background='royalblue')
        
        self.grid_upper_mid.add(_g.Label('Min Limit:'), alignment=2, row_span=1).set_style('font-size: 14pt; font-weight: bold; color: cyan')
        self.numberbox_max = self.grid_upper_mid.add(_g.Button(text=""),
            alignment=2).set_width(20).disable().set_colors(background='limegreen')
        
        
        
        '''
        self.grid_upper_mid.new_autorow()
        
        self.grid_upper_mid.add(_g.Label('Position:'), alignment=1, column = 0).set_style('font-size: 17pt; font-weight: bold; color: cyan')
        
        self.number_mean = self.grid_upper_mid.add(_g.NumberBox(
            value=0, tip='Mean of the count data.'),
            alignment=1, column = 1).set_width(150).disable().set_style('font-size: 17pt; font-weight: bold; color: cyan')
        
        self.grid_upper_mid.new_autorow()
        
        self.grid_upper_mid.add(_g.Label('Test4:'), alignment=1, column = 0).set_style('font-size: 17pt; font-weight: bold; color: coral')
        
        self.number_std = self.grid_upper_mid.add(_g.NumberBox(
            value=0, tip='ggg', decimals = 3),
            alignment=1, column = 1).set_width(150).disable().set_style('font-size: 17pt; font-weight: bold; color: coral')
        '''
        self.window.new_autorow()
        self.grid_bot = self.window.place_object(_g.GridLayout(margins=False), alignment=0).disable()
        
                # Add tabs to the bottom grid
        self.tabs = self.grid_bot.add(_g.TabArea(self.name+'.tabs'), alignment=0)
        
        # Create main tab
        self.tab_2 = self.tabs.add_tab('PMT')
        self.tab_1 = self.tabs.add_tab('Motor')
        
        
        self.tab_1.add(_g.Label('Status:'), alignment=1, row_span=1).set_style('font-size: 17pt; font-weight: bold; color: white')
        self.tab_1.new_autorow()
        
                # Add 

        
        self.tab_1.add(_g.Label('Min Limit:'), alignment=2, row_span=1).set_style('font-size: 14pt; font-weight: bold; color: cyan')
        self.numberbox_min = self.tab_1.add(_g.Button(text=""),
            alignment=1).set_width(20).disable().set_colors(background='limegreen')
        
        self.numberbox_min = self.tab_1.add(_g.NumberBox(value =.23),
            alignment=1).set_width(100).disable().set_style('font-size: 14pt; font-weight: bold; color: cyan')
        
        self.tab_1.new_autorow()
        

        
        
        self.tab_1.add(_g.Label('Max Limit:'), alignment=2, row_span=1).set_style('font-size: 14pt; font-weight: bold; color: cyan')
        self.numberbox_min = self.tab_1.add(_g.Button(text=""),
            alignment=1).set_width(20).disable().set_colors(background='limegreen')
        
        self.numberbox_min = self.tab_1.add(_g.NumberBox(value =147.15),
            alignment=1).set_width(100).disable().set_style('font-size: 14pt; font-weight: bold; color: cyan')
                

        self.tab_1.new_autorow()
        # Add 

        self.button_test = self.tab_1.add(_g.Button(text="Home"),alignment = 1).set_height(30)
        
        self.tab_1.new_autorow()
        
        self.tab_1.add(_g.Label('Control:'), alignment=1, row_span=1).set_style('font-size: 17pt; font-weight: bold; color: white')
        self.tab_1.new_autorow()
        

        
                # Add 
        self.tab_1.add(_g.Label('Target:'), alignment=2, row_span=1).set_style('font-size: 14pt; font-weight: bold; color: cyan')
        self.numberbox_move_target = self.tab_1.add(_g.NumberBox(0, tip='A test.'),
            alignment=2).set_width(100).disable().set_style('font-size: 14pt; font-weight: bold; color: cyan')
        self.tab_1.new_autorow()
        self.tab_1.add(_g.Label('Speed:'), alignment=2, row_span=1).set_style('font-size: 14pt; font-weight: bold; color: cyan')
        self.numberbox_move_speed = self.tab_1.add(_g.NumberBox(0, tip='A test.'),
            alignment=2).set_width(100).disable().set_style('font-size: 14pt; font-weight: bold; color: cyan')
        
        self.tab_1.new_autorow()
        self.button_test = self.tab_1.add(_g.Button(text="Move"),alignment = 1).set_height(30)
        self.tab_1.new_autorow()
        
        

        '''
        # Add data plotting to main tab
        self.plot = self.tab_1.add(_g.DataboxPlot(
            file_type='*.csv',
            autosettings_path=name+'.plot',
            delimiter=',', alignment=0),column_span=10)
        '''

        self.tab_1.set_column_stretch(8, 100)

        
        # Timer for collecting data
        self.timer = _g.Timer(interval_ms=1000, single_shot=False)
        self.timer.signal_tick.connect(self._timer_tick)


if __name__ == '__main__':
    _egg.clear_egg_settings()
    self = Monochrmator()