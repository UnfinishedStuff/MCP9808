# MCP9808

This is a library for running the MCP9808 temperature sensor from Adafruit, including all (?) of the features from the datasheet.
It currently has versions for running the sensor off a PC from [an I2CDriver](https://i2cdriver.com/), from a Raspberry Pi GPIO header and for running on CircuitPython boards.  I may or may not write one for Arduino C.

# Current state

The library is feature complete (?), but hasn't been extensively tested beyond messing around with it when I get a free evening.  Bugs may appear, and I can think of ways it could be written more elegantly.

Just FYI: if you constantly get the same temperature reading make sure you haven't set the shutdown bit to `1`.  That has caught me out.

# Basic use of the script

This is an object-oriented version of the library, so first you have to import the library and then create an instance of the sensor.  

For I2CDriver python this looks like:

    import mcp9808
    sensor = mcp9808.MCP9808(0x18)
  
The function `mcp99808.MCP9808()` can be given an i2c address of the board, but defaults to `0x18`.  Check your breakout for the appropriate default value.

The temperature in °C is returned by the `sensor.readTemp()` function:

    temperature = sensor.readTemp()
    
# Additional functions


<h2>hysteresis(int)</h2>
A function to set the hysteresis.  0 = 0°C (default), 1 = +1.5°C, 2 = +3°C, 3 = +6°C.  Cannot be set when Crit Lock or Win Lock are 1, can be programmed in shutdown mode.  Applies to tUpper, tLower and tCrit, only as temperature drops.  In effect this setting tells the sensor to assume that the real ambient temperature is the sensor temperature minus the hysteresis value, to compensate for temperature dropping faster than the sensor detects.

<h2>shutdown()</h2>
A function to set the shutdown bit.  When set to 1 this disables temperature readings and reduces power consumption.  This state persists until the bit is set to 0 or the power is cycled.  This bit cannot be set to 1 while the winLock or critLock bits are set to 1, but can be returned to 0 while the lock bits are active.

<h2>critLock(int)</h2>
A function to set the Crit Lock bit.  When set to 1 tCrit (and some other registers/bits) cannot be modified.  This bit can only be reset to 0 by a full power cycle reset.
    
<h2>winLock(int)</h2>
A function to set the Win Lock bit.  When set to 1 tUpper and tLower (and some other registers/bits) cannot be modified.  This bit can only be reset to 0 by a full power cycle reset.

<h2>intClear(int)</h2>
A function to set the interrupt clear bit.  When set to 1 this clears the interrupt bit, and reverts to 0.  Cannot be set when the shutdown bit is 1, but will clear when in shutdown mode.

<h2>alertStatus()</h2>
A function to check whether or not an alert is currently being asserted. Returns a 1 (asserted) or a 0.  

<h2>alertControl(int)</h2>
A function to set the Alert Output Control bit.  Setting this to 1 enables the alert output, 0 disables it.  This cannot be modified when either the WinLock or CritLock bits are set.

<h2>alertSelect(int)</h2>
A function to control the Alert Select bit.  This controls when an alert will be asserted.  A value of 0 means that an alert is asserted whenever the temperature passes the upper, lower or critical temperatures.  If set to 1 an alert is only asserted when the temperature is greater than the critical temperature. Cannot be set when Winlock is set.

<h2>alertPolarity(int)</h2>
A function to control the Alert Polarity.  If set to 0 the alert pin is active low (requires a pull-up resistor), if set to 1 the pin is active high. Cannot be altered when winLock or critLock are high.

<h2>alertMode(int)</h2>
A function to control the Alert Mode.  If set to 0 the alert is in comparator mode, if set to 1 the alert is in interrupt mode.  When in comparator mode the alert pin will be asserted (high or low, according to the alertPolarity setting) any time that the ambient temperature exceeds tUpper, tLower or tCrit, depending on the alertSelect bit.  In interrupt mode the alert pin will also be asserted under those conditions, but can be reset to the non-asserted state using the intClear bit. Cannot be altered when winLock or critLock are high.

<h2>setTUpper(int/float)</h2>
Function to set the upper temperature limit of the alert window.  The sensor has a minimum reading of -20°C and an upper of +100°C.  This value has a resolution of 0.25°C.

<h2>setTLower(int/float)</h2>
Function to set the lower temperature limit of the alert window.  The sensor has a minimum reading of -20°C and an upper of +100°C.  This value has a minimum resolution of 0.25°C.

<h2>setTCrit(int/float)</h2>
Function to set the critical temperature limit of the alert window. The sensor has a minimum reading of -20°C and an upper of +100°C.  This value has a minimum resolution of 0.25°C.
 
<h2>getManufacturerID()</h2>
A function to read the manufacturer ID.  Returns a 16 bit value, for the MCP9808 this should read 0x54 (84 decimal).

<h2>getDeviceID()</h2>
A function to read the device ID and revision ID numbers from the MCP9808. Should return a 16 bit value equal to 0x0400.  This function is used in the initialisation of the Class to make sure the device is found when the instance is created.

<h2>setResolution(int)</h2>
A function to set the resolution of the sensor.  Must be given an integer of 0-3 inclusive.  0 = 0.5°C/ 30 ms measurement time, 1 = 0.25°C/ 65 ms, 2 = 0.125°C / 130 ms, 3 = 0.0625°C / 250 ms (default).

<h2>readAlertBits()</h2>
A function to get the interrupt alert bits.  Returns a list of 3 values.

If tA > tCrit then alertBits = [1,0,0]

If tA > tUpper then alertBits = [0,1,0]

If tA < tLower then alertBits = [0,0,1]
