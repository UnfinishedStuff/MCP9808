import i2cdriver
i2c = i2cdriver.I2CDriver("COM41")

"""
Needs to implement bits 13:15 of the temperature register.
"""

class MCP9808:

    
    def __init__(self, deviceAddress = 0x18):
        self.address = deviceAddress
        self.configReg = 0x01
        self.tUpper = 0x02
        self.tLower = 0x03
        self.tCrit = 0x04
        self.temperature = 0x05
        self.manufacturerID = 0x06
        self.deviceID = 0x07
        self.resolution = 0x08

        if (self.getDeviceID() != 0x0400):
            print("WARNING!  Could not detect an MCP9808 at address "\
                  + str(hex(self.address)) + ", check the wiring.\n")


    """
    Internal function to read bytes from the MCP9808.
    """
    def _read(self, register, numBytes, bus = i2c):
        # Open a channel to the device at address "self.address" in write mode
        bus.start(self.address, 0)
        # Point to the register to be read
        bus.write([register])
        # Halt the bus
        bus.stop()
        # Open a channel to the device at address "self.address" in read mode
        bus.start(self.address, 1)
        # Read numBytes bytes of data
        data = i2c.read(numBytes)
        # Stop the bus
        bus.stop()

        return data


    """
    Internal function to write bytes to the MCP9808.
    """
    def _write(self, register, values, bus = i2c):
        # Open a channel to the device at address "self.address" in write mode
        bus.start(self.address, 0)
        # Insert the register address into the start of the values to be written
        values.insert(0, register)
        # Write values to the bus
        bus.write(values)
        # Halt the bus        
        bus.stop()


    #############################
    # Config register functions #
    #############################


    """
    An internal function to get the config register bytes
    """
    def _getConfigReg(self, bus = i2c):
        # Open a channel to the device at address "self.address" in write mode
        bus.start(self.address, 0)
        # Point to the config register
        bus.write([self.configReg])
        # Halt the bus
        bus.stop()
        # Open a channel to the device at address "self.address" in read mode
        bus.start(self.address, 1)
        # Read numBytes bytes of data.  MSB comes first.
        data = list(i2c.read(2))
        bus.stop()

        return data


    """
    A function to set the hysteresis.  0 = 0°C (default), 1 = +1.5°C, 2 = +3°C,
    3 = +6°C.  Cannot be set when Crit Lock or Win Lock are 1, can be
    programmed in shutdown mode.  Applies to tUpper, tLower and tCrit, only as
    temperature drops.  In effect this setting tells the sensor to assume that
    the real ambient temperature is the sensor temperature minus the hysteresis
    value, to compensate for temperature dropping faster than the sensor detects.
    """
    def hysteresis(self, tHyst):
        if isinstance(tHyst, int) and (tHyst >= 0) and (tHyst <= 3):
            # Get the config register bytes
            data = self._getConfigReg()
            # Clear the tHyst bits of the MSB.
            data[0] = data[0] & 0b00000001
            # Merge the MSB with the new tHyst bits
            data[0] = data[0] | (tHyst << 1)
            # Write the new values back to the register
            self._write(self.configReg, data)
        else:
            print("ERROR: tHyst must be an int of 0-3 inclusive.  Value\
 given was " + str(tHyst) + ".")


    """
    A function to set the shutdown bit.  When set to 1 this disables
    temperature readings.  This state persists until the bit is set to 0 or
    the power is cycled.  This bit cannot be set to 1 while the winLock or
    critLock bits are set to 1, but can be returned to 0 while the lock bits
    are active.
    """
    def shutdown(self, shutdown):
        if isinstance(shutdown, int) and ((shutdown == 1) or (shutdown == 0)):
            # Get the config register bytes
            data = self._getConfigReg()
            # Clear the shutdown bit of the MSB.
            data[0] = data[0] & 0b00000110
            # Merge the MSB with the new shutdown bit
            data[0] = data[0] | shutdown
            # Write the new values back to the register
            self._write(self.configReg, data)
        else:
            print("ERROR: shutdown must be given an int of 0-1 inclusive.\
 Value given was " + str(shutdown) + ".")


    """
    A function to set the Crit Lock bit.  When set to 1 tCrit (and some other
    registers/bits) cannot be modified.  This bit can only be reset to 0 by
    a full power cycle reset.
    """
    def critLock(self, critLock):
        if isinstance(critLock, int) and ((critLock == 0) or (critLock == 1)):
            # Get the config register bytes
            data = self._getConfigReg()
            # Clear the critlock bit of the LSB.
            data[1] = data[1] & 0b01111111
            # Merge the LSB with the new critLock bits
            data[1] = data[1] | (critLock << 7)
            # Write the new values back to the register
            self._write(self.configReg, data)
        else:
            print("ERROR: critLock must be given an int of 0-1 inclusive.  \
 Value given was " + str(critLock) + ".")
            

    """
    A function to set the Win Lock bit.  When set to 1 tUpper and tLower (and
    some other registers/bits) cannot be modified.  This bit can only be reset
    to 0 by a full power cycle reset.
    """
    def winLock(self, winLock):
        if isinstance(winLock, int) and ((winLock == 0) or (winLock == 1)):
            # Get the config register bytes
            data = self._getConfigReg()
            # Clear the winLock bit of the LSB.
            data[1] = data[1] & 0b10111111
            # Merge the LSB with the new winLock bits
            data[1] = data[1] | (winLock << 6)
            # Write the new values back to the register
            self._write(self.configReg, data)
        else:
            print("ERROR: winLock must be given an int of 0-1 inclusive.\
 Value given was " + str(winLock) + ".")

        
    """
    A function to set the interrupt clear bit.  When set to 1 this clears the
    interrupt bit, and reverts to 0.  Cannot be set when the shutdown bit is 1,
    but will clear when in shutdown mode.
    """
    def intClear(self, intClear):
        if isinstance(intClear, int) and ((intClear == 0) or (intClear == 1)):
            # Get the config register bytes
            data = self._getConfigReg()
            # Clear the intClear bit of the LSB.
            data[1] = data[1] & 0b11011111
            # Merge the LSB with the new intClear bits
            data[1] = data[1] | (intClear << 5)
            # Write the new values back to the register
            self._write(self.configReg, data)
        else:
            print("ERROR: intClear must be given an int of 0-1 inclusive.\
 Value given was " + str(intClear) + ".")


    """
    A function to check whether or not an alert is currently being asserted.
    Returns a 1 (asserted) or a 0.
    """
    def alertStatus(self):
        # Get the config register bytes
        data = self._getConfigReg()
        alertStatus = (data[1] & 0b00010000) >> 4
        return alertStatus


    """
    A function to set the Alert Output Control bit.  Setting this to 1 enables
    the alert output, 0 disables it.  This cannot be modified when either the
    WinLock or CritLock bits are set.
    """
    def alertControl(self, alertControl):
        if isinstance(alertControl, int) and \
           ((alertControl == 0) or (alertControl == 1)):
            # Get the config register bytes
            data = self._getConfigReg()
            # Clear the alertControl bit of the LSB.
            data[1] = data[1] & 0b11110111
            # Merge the LSB with the new alertControl bits
            data[1] = data[1] | (alertControl << 3)
            # Write the new values back to the register
            self._write(self.configReg, data)
        else:
            print("ERROR: alertControl must be given an int of 0-1 inclusive.\
 Value given was " + str(alertControl) + ".")
    

    """
    A function to control the Alert Select bit.  This controls when an alert
    will be asserted.  A value of 0 means that an alert is asserted whenever
    the temperature passes the upper, lower or critical temperatures.  If set
    to 1 an alert is only asserted when the temperature is greater than the
    critical temperature.
    Cannot be set when Winlock is set.
    """
    def alertSelect(self, alertSelect):
        if isinstance(alertSelect, int) and \
           ((alertSelect == 0) or (alertSelect == 1)):
            # Get the config register bytes
            data = self._getConfigReg()
            # Clear the alertSelect bit of the LSB.
            data[1] = data[1] & 0b11111011
            # Merge the LSB with the new alertSelect bits
            data[1] = data[1] | (alertSelect << 2)
            # Write the new values back to the register
            self._write(self.configReg, data)
        else:
            print("ERROR: alertSelect must be an int of 0-1 inclusive.  Value\
 given was " + str(alertSelect) + ".")


    """
    A function to control the Alert Polarity.  If set to 0 the alert pin is
    active low (requires a pull-up resistor), if set to 1 the pin is active
    high.
    Cannot be altered when winLock or critLock are high.
    """
    def alertPolarity(self, alertPolarity):
        if isinstance(alertPolarity, int) and\
           ((alertPolarity == 0) or (alertPolarity == 1)):
            # Get the config register bytes
            data = self._getConfigReg()
            # Clear the alertPolarity bit of the LSB.
            data[1] = data[1] & 0b11111101
            # Merge the LSB with the new alertPolarity bits
            data[1] = data[1] | (alertPolarity << 1)
            # Write the new values back to the register
            self._write(self.configReg, data)
        else:
            print("ERROR: alertPolarity must be an int of 0-1 inclusive.  Value\
 given was " + str(alertPolarity) + ".")


    """
    A function to control the Alert Mode.  If set to 0 the alert is in
    comparator mode, if set to 1 the alert is in interrupt mode.  When in
    comparator mode the alert pin will be asserted (high or low, according to
    the alertPolarity setting) any time that the ambient temperature exceeds
    tUpper, tLower or tCrit, depending on the alertSelect bit.  In interrupt
    mode the alert pin will also be asserted under those conditions, but can
    be reset to the non-asserted state using the intClear bit.
    Cannot be altered when winLock or critLock are high.
    """
    def alertMode(self, alertMode, bus = i2c):
        if isinstance(alertMode, int) and \
           ((alertMode == 0) or (alertMode == 1)):
            # Get the config register bytes
            data = self._getConfigReg()
            # Clear the alertMode bit of the LSB.
            data[1] = data[1] & 0b11111110
            # Merge the LSB with the new critLock bits
            data[1] = data[1] | alertMode
            # Write the new values back to the register
            self._write(self.configReg, data)
        else:
            print("ERROR: alertMode must be a value of 0-1 inclusive.  Value\
 given was " + str(alertMode) + ".")


    ########################
    # Config functions end #
    ########################

    """
    A function to convert negative ints/floats provided by the user to a value
    suitable for writing to the tUpper, tLower and tCrit registers
    """
    def _valueToTwosComplementNegative(self, value):
        # Convert to number of whole 0.25°C increments
        value = int(abs(value) / 0.25)
        # Convert to twos complement
        value = (1023 - value) - 1
        # Add a negative sign bit
        value = value | 1024

        return(value)


    """
    Function to set the upper temperature limit of the alert window.  The sensor
    has a minimum reading of -20°C and an upper of +100°C.  This value has a
    resolution of 0.25°C.
    """
    def setTUpper(self, tUpper, bus = i2c):
        if (isinstance(tUpper, int) or isinstance(tUpper, float)) and\
           ((tUpper >= -20) and (tUpper <= 100)):
            # If the value is negative, convert to a twos complement negative
            if (tUpper < 0):
                value = self._valueToTwosComplementNegative(tUpper)
            else:
                # Convert to number of whole 0.25°C increments
                value = int(tUpper / 0.25)
            # bitshift to take into account unused bits.
            value = value << 2
            # Write to the bus
            self._write(self.tUpper, [value >> 8, value & 0xFF])
        else:
            print("ERROR: setTUpper must be given an int or float from -20 to\
 100 inclusive.  Value given was " + str(tUpper) + ".")


    """
    Debug function to read the tUpper register and make sure it is being
    written to properly.
    """
    def _readTUpper(self):
        # Get the bytes holding tUpper
        data = list(self._read(self.tUpper, 2))
        # print("As read:")
        # print(bin(data[0]), bin(data[1]))
        # Combine the two bytes, bitshift right 2 to get rid of unused bits
        value = ((data[0] << 8) + data[1]) >> 2

        #print(bin(value))
        # If the sign bit is high (i.e. the value is negative)
        if ((value & 1024) == 1024):
            # Get rid of the sign bit
            value = value - 1024
            #print(bin(value))
            # Convert two's complement binary to a standard binary value
            value = (1023 - value) - 1
            # Convert to a Celsius temperature and add a negative sign
            return(-(value/4))

        else:
            # Convert to celsius
            return(value/4)


    """
    Function to set the lower temperature limit of the alert window.  The sensor
    has a minimum reading of -20°C and an upper of +100°C.  This value has a
    minimum resolution of 0.25°C.
    """
    def setTLower(self, tLower, bus = i2c):
        if ((isinstance(tLower, int)) or (isinstance(tLower, float))) and\
           ((tLower >= -20) and (tLower <= 100)):
            # Value will be processed to twos complement.

            # If the value is negative, convert to a twos complement value
            if (tLower < 0):
                value = self._valueToTwosComplementNegative(tLower)
            else:
                # Convert to number of whole 0.25°C increments
                value = int(tLower / 0.25)
            # bitshift to take into account unused bits.
            value = value << 2
            # Write to the bus
            self._write(self.tLower, [value >> 8, value & 0xFF])
        else:
            print("ERROR: setTLower must be given an int or float from -20 to\
 100 inclusive.  Value given was " + str(tLower) + ".")



    """
    Debug function to read the tLower register and make sure it is being
    written to properly.
    """
    def readTLower(self):
        # Get the bytes holding tLower
        data = list(self._read(0x03, 2))
        # print("As read:")
        # print(bin(data[0]), bin(data[1]))
        # Combine the two bytes, bitshift right 2 to get rid of unused bits
        value = ((data[0] << 8) + data[1]) >> 2

        #print(bin(value))
        # If the sign bit is high (i.e. the value is negative)
        if ((value & 1024) == 1024):
            # Get rid of the sign bit
            value = value - 1024
            #print(bin(value))
            # Convert two's complement binary to a standard binary value
            value = (1023 - value) - 1
            # Convert to a Celsius temperature and add a negative sign
            return(-(value/4))

        else:
            # Convert to celsius
            return(value/4)


    """
    Function to set the critical temperature limit of the alert window.
    The sensor has a minimum reading of -20°C and an upper of +100°C.  This
    value has a minimum resolution of 0.25°C.
    """
    def setTCrit(self, tCrit, bus = i2c):
        if (isinstance(tCrit, int) or isinstance(tCrit, float)) and\
            ((tCrit >= -20) and (tCrit <= 100)):
            # If the value is negative, convert to a twos complement value
            if (tCrit < 0):
                value = self._valueToTwosComplementNegative(tCrit)
            else:
                # Convert to number of whole 0.25°C increments
                value = int(tCrit / 0.25)
            # bitshift to take into account unused bits.
            value = value << 2
            # Write to the bus
            self._write(self.tCrit, [value >> 8, value & 0xFF])
        else:
            print("ERROR: setTCrit must be given an int or float from -20 to\
 100 inclusive.  Value given was " + str(tCrit) + ".")



    """
    Debug function to read the tCrit register and make sure it is being
    written to properly.
    """
    def readTCrit(self):
        # Get the bytes holding tLower
        data = list(self._read(0x04, 2))
        # print("As read:")
        # print(bin(data[0]), bin(data[1]))
        # Combine the two bytes, bitshift right 2 to get rid of unused bits
        value = ((data[0] << 8) + data[1]) >> 2

        #print(bin(value))
        # If the sign bit is high (i.e. the value is negative)
        if ((value & 1024) == 1024):
            # Get rid of the sign bit
            value = value - 1024
            #print(bin(value))
            # Convert two's complement binary to a standard binary value
            value = (1023 - value) - 1
            # Convert to a Celsius temperature and add a negative sign
            return(-(value/4))

        else:
            # Convert to celsius
            return(value/4)


    """
    Function to read the temperature.  Returns a float of temperature in
    degrees Celsius.
    """
    def readTemp(self):
        # Get the bytes holding the temperature
        data = list(self._read(self.temperature, 2))
        # Combine the two bytes, mask bits 14-16
        value = ((data[0] << 8) + data[1]) & 0x1fff

        #print(bin(value))
        # If the sign bit is high (i.e. the value is negative)
        if ((value & 4096) == 4096):
            # Get rid of the sign bit
            value = value - 4096
            #print(bin(value))
            # Convert two's complement binary to a standard binary value
            value = (4095 - value) - 1
            # Convert to a Celsius temperature and add a negative sign
            return(-(value * 0.0625))

        else:
            # Convert to celsius
            return(value * 0.0625)


    """
    A function to read the manufacturer ID.  For the MCP9808, this should read
    0x54 (84 decimal).
    """
    def getManufacturerID(self):
        values = list(self._read(self.manufacturerID, 2))
        manufID = (values[0] << 8) + values[1]
        return(manufID)


    """
    A function to read the device ID and revision ID numbers from the MCP9808.
    Should return 0x0400.  This function is used in the initialisation of the
    Class to make sure the device is found when the instance is created.
    """
    def getDeviceID(self):
        value = list(self._read(self.deviceID, 2))
        deviceID = (value[0] << 8) + value[1]
        return(deviceID)



    """
    A function to set the resolution of the sensor.  Must be given an integer
    of 0-3 inclusive.  0 = 0.5°C/ 30 ms measurement time, 1 = 0.25°C/ 65 ms,
    2 = 0.125°C / 130 ms, 3 = 0.0625°C / 250 ms (default).
    """
    def setResolution(self, resolution):
        # Check that the requested resolution is an integer
        if isinstance(resolution, int):
            #Check that the requested resolution is between 0 and 3 inclusive
            if ((resolution >= 0) and (resolution <= 3)):
                self.write(self.resolution, resolution)
            else:
                print("ERROR: resolution must be an integer between 0 and 3.  \
Value given was " + str(resolution) + ".")
        else:
            print("ERROR: resolution must be an integer between 0 and 3.  Value\
 given was " + str(resolution) + ".")



    """
    A function to get the interrupt alert bits.
    If tA > tCrit then alertBits = [1,0,0]
    If tA > tUpper then alertBits = [0,1,0]
    If tA < tLower then alertBits = [0,0,1]
    """
    def readAlertBits(self):
        # Get the bytes holding the temperature
        data = list(self._read(self.temperature, 2))
        # Combine the two bytes, mask bits 14-16
        value = data[0] >> 5
        alertBits = [0,0,0]
        if  ((value & 0b1) == 0b1):
            alertBits[2] = 1
        if  ((value & 0b10) == 0b10):
            alertBits[1] = 1
        if  ((value & 0b100) == 0b100):
            alertBits[0] = 1

        return alertBits

    
