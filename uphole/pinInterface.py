import machine
from inputPins import get_label_from_pin
from inputPins import input_types
from inputPins import interrupt_types

# Class to abstract and manage GPIO input pins (both regular and interrupt types)
class Input_Pin_Interface:
    def __init__(self, GPIO_num, input_type):  
        # Get label for the GPIO number using utility function
        self.label = get_label_from_pin(GPIO_num)
        self.gpio_num = GPIO_num

        # Check if a valid label was found
        if self.label is None:
            print('Wrong pin number inputted %d' % (GPIO_num))
            return

        # Check for valid input type
        if input_type in input_types:
            if input_type == 'REGULAR':
                # Configure as a regular input pin
                self.pin = machine.Pin(GPIO_num, machine.Pin.IN)
            else:
                # Interrupt pins must be explicitly set up using setUpInterrupt
                print('This pin must be an interrupt. Set properly')
        else:
            print('Wrong input type inputted %s' % (input_type))
            return
        
    # Method to configure the pin as an interrupt with a specified edge and handler
    def setUpInterrupt(self, handler, interrupt_type):
        if interrupt_type in interrupt_types:
            if interrupt_type == 'FALLING':
                # Set up pin with pull-up resistor and falling edge interrupt
                self.pin = machine.Pin(self.gpio_num, machine.Pin.IN, machine.Pin.PULL_UP)
                self.pin.irq(trigger=machine.Pin.IRQ_FALLING, handler=handler)
            else:
                # Set up pin with pull-down resistor and rising edge interrupt
                self.pin = machine.Pin(self.gpio_num, machine.Pin.IN, machine.Pin.PULL_DOWN)
                self.pin.irq(trigger=machine.Pin.IRQ_RISING, handler=handler)
        else:
            print('Wrong interrupt type inputted %s' % (interrupt_type))
        
    # Returns True if the pin reads HIGH
    def isHigh(self):
        return self.pin.value() == 1
    
    # Returns True if the pin reads LOW
    def isLow(self):
        return self.pin.value() == 0
