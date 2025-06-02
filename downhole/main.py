from rgb import RGB_Sensor           # Import RGB sensor class
from led import LED                 # Import LED control class
from dac4to20 import DAC_4to20     # Import DAC class for 4–20 mA output

import time

# === CONSTANTS ===

PERIPHERAL_FREQ = 100000              # I2C frequency for peripherals (in Hz)

# GPIO pin assignments
RGB_SENSOR_SDA_PIN = 16              # SDA pin for RGB sensor
RGB_SENSOR_SCL_PIN = 17              # SCL pin for RGB sensor
DAC_SDA_PIN        = 18              # SDA pin for DAC
DAC_SCL_PIN        = 19              # SCL pin for DAC

# Timing constants
INIT_WAIT_SECS         = 2           # Delay before main logic starts (to allow peripherals to power up)
MEASUREMENT_LATENCY_MS = 10          # Delay between measurements (in milliseconds)

# Color channel identifiers
RED   = 1
GREEN = 2
BLUE  = 3


class Chalk_Detector:
    def __init__(self):
        """
        Initialize the Chalk Detector system, setting up:
        - RGB color sensor via I2C
        - 4-20 mA DAC output via I2C
        - LED for illumination or indication via PWM
        """
        self.rgbSensor = RGB_Sensor(RGB_SENSOR_SCL_PIN, RGB_SENSOR_SDA_PIN, PERIPHERAL_FREQ, 0)
        self.dac       = DAC_4to20(DAC_SCL_PIN, DAC_SDA_PIN, PERIPHERAL_FREQ, 1)

    def main(self):
        """
        Main loop of the Chalk Detector:
        - Turns on the LED
        - Continuously reads the BLUE channel value from the RGB sensor
        - Sends the corresponding value to the DAC as a current output
        """
        self.dac.begin()       # Initialize communication with DAC

        while True:
            # Read BLUE intensity in mA from RGB sensor and output via DAC
            self.dac.output(self.rgbSensor.read_colour_mA(BLUE))
            time.sleep_ms(MEASUREMENT_LATENCY_MS)  # Small delay to limit sampling rate


if __name__ == "__main__":
    # Wait for devices to settle before starting main logic
    time.sleep(INIT_WAIT_SECS)
    chalkDetector = Chalk_Detector()
    chalkDetector.main()
