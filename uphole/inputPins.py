# Dictionary mapping labels to specific GPIO pin numbers
input_pins = {
    'DPT_RST': 9,   # Depth Reset button connected to pin 9
    'DPT_IN':  10,  # Depth Increment signal connected to pin 10
    'ENA_IN':  11   # Enable signal connected to pin 11
}

# List of possible input pin types
input_types = [
    'REGULAR',     # Standard digital input pin
    'INTERRUPT'    # Interrupt-based input pin
]

# List of interrupt trigger types
interrupt_types = [
    'RISING',      # Interrupt triggered on rising edge (LOW to HIGH)
    'FALLING'      # Interrupt triggered on falling edge (HIGH to LOW)
]

# Utility function to return the label associated with a given pin number
def get_label_from_pin(pin_number):
    for label, number in input_pins.items():
        if number == pin_number:
            return label  # Return the corresponding label if found
    return None  # Return None if no matching pin is found
