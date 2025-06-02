import machine

# Constants for ADC conversion
ADC_MAX_VOLTAGE = 3.3        # Reference voltage for ADC (typically 3.3V on RP2040)
ADC_MAX_READING = 0xFFFF     # 16-bit maximum value for ADC (65535)

class ADC_Reader:
    def __init__(self, adc1_pin, adc2_pin):
        # Initialize ADC objects on the specified pins
        self.adc1 = machine.ADC(adc1_pin)
        self.adc2 = machine.ADC(adc2_pin)
    
    def measure_counts(self):
        # Read raw 16-bit ADC values from both pins
        adc1_val = self.adc1.read_u16()
        adc2_val = self.adc2.read_u16()
        
        # Compute the absolute voltage difference between the two ADC readings
        return abs(adc1_val - adc2_val)

    def print_voltage_drop(self):
        # Print the calculated voltage drop to the console
        print('Current voltage drop is', self.measure_voltage_drop())
