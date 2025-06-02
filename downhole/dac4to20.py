import machine
import time

# Default I2C address and register for the GP8302 DAC
GP8302_DEF_I2C_ADDR       = 0x58
GP8302_CONFIG_CURRENT_REG = 0x02           # Register to write current output value
GP8302_CURRENT_RESOLUTION = 0x0FFF         # 12-bit resolution (4095)
GP8302_MAX_CURRENT        = 25             # Max output current is 25mA

# Values used to store the current DAC configuration to non-volatile memory
GP8302_STORE_TIMING_HEAD  = 0x02
GP8302_STORE_TIMING_ADDR  = 0x10
GP8302_STORE_TIMING_CMD1  = 0x03
GP8302_STORE_TIMING_CMD2  = 0x00
GP8302_STORE_TIMING_DELAY = 0.01           # Delay after issuing store command

# Bit-banged I2C timing constants (in seconds)
I2C_CYCLE_TOTAL           = 0.000005
I2C_CYCLE_BEFORE          = 0.000002
I2C_CYCLE_AFTER           = 0.000003

class DAC_4to20:
    def __init__(self, scl_pin, sda_pin, freq, id):
        # Initialize standard hardware I2C for device detection
        self.i2c = machine.I2C(id,
                  sda=machine.Pin(sda_pin),
                  scl=machine.Pin(scl_pin),
                  freq=freq)

        # Also configure pins manually for bit-banging I2C
        self._scl = machine.Pin(scl_pin, machine.Pin.OUT, value=1)
        self._sda = machine.Pin(sda_pin, machine.Pin.OUT, value=1)

        self._addr = GP8302_DEF_I2C_ADDR

        # Default DAC values for 4mA and 20mA calibration
        self._dac_4 = 655
        self._dac_20 = 3277

        self._calibration = False   # Flag to determine if custom calibration is enabled
        self._digital = 0           # Current digital DAC value being output

    # Delay to match I2C timing spec
    def _i2c_delay(self):
        time.sleep(I2C_CYCLE_TOTAL)

    # Send I2C start condition
    def _start_signal(self):
        self._sda.value(1)
        self._scl.value(1)
        time.sleep(I2C_CYCLE_BEFORE)
        self._sda.value(0)
        time.sleep(I2C_CYCLE_AFTER)
        self._scl.value(0)

    # Send I2C stop condition
    def _stop_signal(self):
        self._sda.value(0)
        self._scl.value(1)
        time.sleep(I2C_CYCLE_BEFORE)
        self._sda.value(1)
        time.sleep(I2C_CYCLE_AFTER)

    # Send a byte over I2C manually (bit-banged)
    def _send_byte(self, data, delay=True):
        for i in range(8):
            self._sda.value((data >> (7 - i)) & 0x01)
            self._scl.value(1)
            if delay:
                time.sleep(I2C_CYCLE_TOTAL)
            self._scl.value(0)
        
        # Read ACK bit from slave
        self._sda.init(machine.Pin.IN)
        self._scl.value(1)
        ack = self._sda.value()
        self._scl.value(0)
        self._sda.init(machine.Pin.OUT)
        return ack

    # Check if device is reachable over I2C
    def begin(self):
        self._start_signal()
        if self._send_byte(self._addr << 1):  # Write address
            self._stop_signal()
            return 2  # Device not found
        self._stop_signal()
        return 0  # Success

    # Apply custom 4–20mA calibration values
    def calibration4_20mA(self, dac_4, dac_20):
        if dac_4 >= dac_20 or dac_20 > GP8302_CURRENT_RESOLUTION:
            return  # Invalid calibration range
        self._dac_4 = dac_4
        self._dac_20 = dac_20
        self._calibration = True

    # Output raw DAC value and return actual current in mA
    def output_mA(self, dac):
        self._digital = dac & GP8302_CURRENT_RESOLUTION

        self._start_signal()
        self._send_byte(self._addr << 1)  # Device address
        self._send_byte(GP8302_CONFIG_CURRENT_REG)  # Register to configure current
        
        # Send lower and upper parts of the 12-bit value in two bytes
        self._send_byte((self._digital << 4) & 0xF0)  # Lower nibble is shifted
        self._send_byte((self._digital >> 4) & 0xFF)  # Upper bits

        self._stop_signal()

        # Return corresponding current output in mA
        return (self._digital / GP8302_CURRENT_RESOLUTION) * GP8302_MAX_CURRENT

    # Output a specific current in mA (auto convert to DAC value)
    def output(self, current_mA):
        # Clamp requested current between 0 and max allowed
        current_mA = min(max(current_mA, 0), GP8302_MAX_CURRENT)

        if self._calibration and 4 <= current_mA <= 20:
            # Use custom calibrated DAC range
            self._digital = self._dac_4 + ((current_mA - 4) * (self._dac_20 - self._dac_4)) // 16
        else:
            # Linearly scale current to DAC range
            self._digital = int((current_mA * GP8302_CURRENT_RESOLUTION) / GP8302_MAX_CURRENT)

        self.output_mA(self._digital)
        return self._digital

    # Store current DAC setting into EEPROM
    def store(self):
        # Store command sequence required by GP8302
        self._start_signal()
        self._send_byte(GP8302_STORE_TIMING_HEAD)
        self._stop_signal()

        self._start_signal()
        self._send_byte(GP8302_STORE_TIMING_ADDR)
        self._send_byte(GP8302_STORE_TIMING_CMD1)
        self._stop_signal()

        self._start_signal()
        self._send_byte(self._addr << 1)
        for _ in range(8):
            self._send_byte(GP8302_STORE_TIMING_CMD2)
        self._stop_signal()

        # Wait for write cycle to complete
        time.sleep(GP8302_STORE_TIMING_DELAY)
