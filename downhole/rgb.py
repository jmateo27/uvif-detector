import machine
import time

# === CONSTANTS ===

# Current output range for DAC (used to convert sensor values to 4–20 mA)
CURRENT_MIN_mA      = 4.0                            # Minimum current in mA
CURRENT_MAX_mA      = 20.0                           # Maximum current in mA
CURRENT_RANGE_mA    = CURRENT_MAX_mA - CURRENT_MIN_mA

# VEML3328 I2C address and register constants
VEML3328_ADDR        = 0x10                          # I2C address of the VEML3328 RGB sensor
VEML3328_DEV_ID      = 0x28                          # Device ID (not used here but useful for validation)
VEML3328_R_ADDR      = 0x05                          # Red channel register
VEML3328_G_ADDR      = 0x06                          # Green channel register
VEML3328_B_ADDR      = 0x07                          # Blue channel register
REG_CONTROL          = 0x00                          # Control register
CONFIG_VALUE         = b'\x00\x00'                   # Default configuration (power on / normal mode)
VEML3328_MAX_READING = 65536                         # Max value for 16-bit register (used for normalization)

# Color codes for function input
RED   = 1
GREEN = 2
BLUE  = 3

# Custom scaling for blue channel (empirical or expected max reading)
BLUE_MAX_READING = 4000


class RGB_Sensor:
    def __init__(self, scl_pin, sda_pin, freq, id):
        """
        Initialize the RGB sensor over I2C.
        Arguments:
        - scl_pin, sda_pin: GPIO pins for I2C
        - freq: I2C communication frequency
        - id: I2C bus ID (0 or 1 depending on board)
        """
        self.i2c = machine.I2C(id,
                               sda=machine.Pin(sda_pin),
                               scl=machine.Pin(scl_pin),
                               freq=freq)

        # Write configuration to control register
        self.i2c.writeto_mem(VEML3328_ADDR, REG_CONTROL, CONFIG_VALUE)
        time.sleep(0.1)  # Short delay to allow sensor to stabilize

    def reg_readword_from(self, colour_reg):
        """
        Read 2 bytes (16 bits) from a given color register and return as an integer.
        """
        data = self.i2c.readfrom_mem(VEML3328_ADDR, colour_reg, 2)
        value = data[0] | (data[1] << 8)  # Little-endian conversion
        return value

    def read_colour_raw(self, colour):
        """
        Get raw color reading (0-65535) from the sensor.
        Arguments:
        - colour: use RED, GREEN, or BLUE constants
        """
        # Determine register address based on color
        if colour == RED:
            colour_addr = VEML3328_R_ADDR
        elif colour == GREEN:
            colour_addr = VEML3328_G_ADDR
        elif colour == BLUE:
            colour_addr = VEML3328_B_ADDR
        else:
            print('Cannot read this colour with code ', colour)
            return 0

        return self.reg_readword_from(colour_addr)

    def read_colour_mA(self, colour):
        """
        Convert raw sensor reading to a 4–20 mA current value.
        Arguments:
        - colour: use RED, GREEN, or BLUE constants

        Returns:
        - float current in mA proportional to the light intensity
        """
        raw_reading = self.read_colour_raw(colour)

        # Blue channel uses a different expected maximum for scaling
        if colour == BLUE:
            return raw_reading / BLUE_MAX_READING * CURRENT_RANGE_mA + CURRENT_MIN_mA
        else:
            return raw_reading / VEML3328_MAX_READING * CURRENT_RANGE_mA + CURRENT_MIN_mA
