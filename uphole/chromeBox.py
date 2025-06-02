# Import custom modules and libraries for ADC reading and pin interface handling
from adcReader import ADC_Reader
from pinInterface import Input_Pin_Interface
from inputPins import input_pins

import time
import machine

# ----------------------------- CONSTANTS ---------------------------------
ADC1_PIN                    = 28        # First ADC pin used for voltage measurement
ADC2_PIN                    = 27        # Second ADC pin, likely unused in this file

INIT_WAIT_SECS              = 3.0       # Delay before starting measurements
MEASUREMENT_LATENCY_SECS    = 5.0       # Delay between measurements

LOAD_RESISTOR_OHMS          = 150.0     # Resistance used in current calculation
A_to_mA                     = 1000.0    # Conversion factor from A to mA

DEPTH_INCREMENT_M           = 0.025     # Meters added to depth on each depth signal
CYCLE_LATENCY_MS            = 1         # Not used in this script
DEBOUNCE_MS                 = 200       # Time to avoid repeated button press events

DATA_FILE					= 'chromeData.csv'  # Output data file name

# ----------------------------- MAIN CLASS --------------------------------
class ChokBaux:
    def __init__(self):
        # Initialize ADC reader and input pin interfaces
        self.adc            = ADC_Reader(ADC1_PIN, ADC2_PIN)
        self.dpt_rst_in     = Input_Pin_Interface(input_pins['DPT_RST'], 'INTERRUPT')
        self.dpt_in         = Input_Pin_Interface(input_pins['DPT_IN'], 'INTERRUPT')
        self.ena_in         = Input_Pin_Interface(input_pins['ENA_IN'], 'REGULAR')
        
        # Initialize timers for managing events
        self.timer1         = machine.Timer()
        self.timer2         = machine.Timer()
        
        # Track last button press time to debounce
        self.last_trigger_time = 0
        
        # Initialize depth count
        self.depth_count    = 0

    # Converts ADC counts to voltage (in Volts)
    def counts_to_voltage_drop_V(self, counts):
        return counts * self.adc.ADC_MAX_VOLTAGE / self.adc.ADC_MAX_READING
    
    # Converts ADC counts to current (in milliamps)
    def counts_to_current_consumption_mA(self, counts):
        return self.counts_to_voltage_drop_V(counts) * A_to_mA / LOAD_RESISTOR_OHMS

    # Continuously collect voltage and current data and log to file
    def collectData(self):
        time.sleep(INIT_WAIT_SECS)
        while True:
            with open('data.txt', 'w') as file:
                c = self.adc.measure_counts()
                v = self.counts_to_voltage_drop_V(c)
                i = self.counts_to_current_consumption_mA(c)
                print("Voltage = %f V\nCurrent = %f mA\n# Counts = %d\n\n" % (v, i, c))
                file.write("%f\t%f\t%d\n" % (v, i, c))
                time.sleep(MEASUREMENT_LATENCY_SECS)

    # Collects a fixed number of samples for paint testing purposes
    def collectPaintSampleData(self):
        print("3 seconds to begin, get paint sample 01 ready...")
        time.sleep(INIT_WAIT_SECS)
        with open('uphole_data_45m.txt', 'w') as file:
            for x in range(1, 23):  # Collect 22 samples
                c = self.adc.measure_counts()
                v = self.counts_to_voltage_drop_V(c)
                i = self.counts_to_current_consumption_mA(c)
                print("Paint sample %d:\nVoltage = %f V\nCurrent = %f mA\n# Counts = %d\n\n" % (x, v, i, c))
                file.write("%d\t%f\t%f\t%d\n" % (x, v, i, c))
                time.sleep(MEASUREMENT_LATENCY_SECS)

    # Resets depth count to 0 when reset switch is triggered
    def depth_reset_timer_callback(self, t):
        self.depth_count = 0

    # Debounced interrupt handler for resetting depth
    def depth_reset_handler(self, pin):
        current_time = time.ticks_ms()
        if time.ticks_diff(current_time, self.last_trigger_time) > DEBOUNCE_MS:
            if self.dpt_rst_in.isHigh():
                print('Depth reset switch flipped. Setting depth back to 0 m')
                self.last_trigger_time = current_time
                self.timer2.init(mode=machine.Timer.ONE_SHOT, period=DEBOUNCE_MS, callback=self.depth_reset_timer_callback)

    # Timer callback that logs current depth, voltage, and current
    def depth_timer_callback(self, t):
        self.depth_count += DEPTH_INCREMENT_M
        c = self.adc.measure_counts()
        v = self.counts_to_voltage_drop_V(c)
        i = self.counts_to_current_consumption_mA(c)
        print("Depth = %.3f m\tVoltage = %f V\tCurrent = %f mA\t# Counts = %d\n\n" % (self.depth_count, v, i, c))
        with open(DATA_FILE, 'a') as file:
            file.write("%.3f,%f,%f,%d\n" % (self.depth_count, v, i, c))
            file.flush()

    # Interrupt handler that triggers a timed depth update if enabled
    def depth_input_handler(self, pin):
        if self.ena_in.isLow():  # Only log depth if ENA_IN is LOW
            self.timer1.init(mode=machine.Timer.ONE_SHOT, period=10, callback=self.depth_timer_callback)

    # Main execution method: sets up interrupts and starts logging
    def main(self):
        time.sleep(INIT_WAIT_SECS)
        
        # Write header to data file
        with open(DATA_FILE, 'w') as file:
            file.write("Depth(m),Voltage(V),Current(mA),# Counts\n")
            file.flush()
        
        # Attach interrupt handlers
        self.dpt_rst_in.setUpInterrupt(self.depth_reset_handler, 'RISING')
        self.dpt_in.setUpInterrupt(self.depth_input_handler, 'FALLING')

        print("ChromeBox is in action!\n")

# -------------------------- SCRIPT ENTRY POINT ---------------------------
if __name__ == "__main__":
    chokBaux = ChokBaux()
    chokBaux.main()
