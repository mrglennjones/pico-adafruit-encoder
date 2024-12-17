'''
this is a pimoroni pico plus 2w tester for the Adafruit I2C Stemma QT Rotary Encoder Breakout with NeoPixel - STEMMA QT / Qwiic

https://www.adafruit.com/product/4991

it doesnt quite work apart from the encoder button being pressed down does return a different delta value, but thats all.
no encoder value can be read not the neopixel rgb led can be set.
'''

from machine import Pin, I2C
import time

# I2C Initialization for Qwiic Port
i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=100000)  # Qwiic pins: GP4 (SDA), GP5 (SCL)
ENCODER_ADDR = 0x36  # I2C address for Seesaw devices

# Seesaw Register Definitions
GPIO_BASE = 0x01
SEESAW_GPIO_BULK = 0x04
BUTTON_PIN = 24  # Button pin is on GPIO 24

ENCODER_BASE = 0x11
SEESAW_ENCODER_POSITION = 0x00
SEESAW_ENCODER_DELTA = 0x01

NEOPIXEL_BASE = 0x0E
SEESAW_NEOPIXEL_SET = 0x03

# Function 1: Read and Analyze Button State
def read_button_state_debug():
    """Read and print all GPIO pin states, including button pin analysis."""
    try:
        # Request GPIO bulk data
        i2c.writeto(ENCODER_ADDR, bytearray([GPIO_BASE, SEESAW_GPIO_BULK]))
        time.sleep(0.01)
        data = i2c.readfrom(ENCODER_ADDR, 4)

        print(f"Raw GPIO Data: {[hex(b) for b in data]}")
        
        # Loop through all pins (24–31 in the last byte)
        for pin in range(24, 32):
            bit = (data[3] >> (pin - 24)) & 0x01
            print(f"Pin {pin}: {'HIGH' if bit else 'LOW'}")

        # Check the button pin specifically
        button_bit = (data[3] >> (BUTTON_PIN - 24)) & 0x01
        print(f"Button Pin {BUTTON_PIN}: {'Pressed' if not button_bit else 'Released'}")
    except Exception as e:
        print(f"Error reading button state: {e}")

# Function 2: Test NeoPixel LED
def set_neopixel_color(red, green, blue):
    """Set the NeoPixel color."""
    try:
        i2c.writeto(ENCODER_ADDR, bytearray([NEOPIXEL_BASE, SEESAW_NEOPIXEL_SET, red, green, blue, 0xFF]))
        print(f"NeoPixel set to RGB({red}, {green}, {blue})")
        time.sleep(0.1)
    except Exception as e:
        print(f"Error setting NeoPixel color: {e}")

def test_neopixel():
    print("Testing NeoPixel...")
    set_neopixel_color(255, 0, 0)  # Red
    time.sleep(1)
    set_neopixel_color(0, 255, 0)  # Green
    time.sleep(1)
    set_neopixel_color(0, 0, 255)  # Blue
    time.sleep(1)
    print("NeoPixel test complete.")

# Function 3: Test Encoder Position and Delta
def read_encoder_position():
    """Read the encoder's absolute position."""
    try:
        i2c.writeto(ENCODER_ADDR, bytearray([ENCODER_BASE, SEESAW_ENCODER_POSITION]))
        time.sleep(0.01)
        data = i2c.readfrom(ENCODER_ADDR, 4)
        position = (data[0] << 24) | (data[1] << 16) | (data[2] << 8) | data[3]
        if position & (1 << 31):  # Handle two's complement
            position -= 1 << 32
        return position
    except Exception as e:
        print(f"Error reading encoder position: {e}")
        return None

def read_encoder_delta():
    """Read the encoder's relative delta."""
    try:
        i2c.writeto(ENCODER_ADDR, bytearray([ENCODER_BASE, SEESAW_ENCODER_DELTA]))
        time.sleep(0.01)
        data = i2c.readfrom(ENCODER_ADDR, 4)
        delta = (data[0] << 24) | (data[1] << 16) | (data[2] << 8) | data[3]
        if delta & (1 << 31):  # Handle two's complement
            delta -= 1 << 32
        return delta
    except Exception as e:
        print(f"Error reading encoder delta: {e}")
        return None

def test_encoder():
    print("Testing Encoder Position and Delta...")
    try:
        while True:
            position = read_encoder_position()
            delta = read_encoder_delta()
            print(f"Encoder Position: {position}, Encoder Delta: {delta}")
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Encoder test stopped.")

# Main Menu
try:
    while True:
        print("\n--- Seesaw Rotary Encoder Full Test ---")
        print("1. Test Button State")
        print("2. Test NeoPixel LED")
        print("3. Test Encoder Position and Delta")
        print("4. Exit")
        choice = input("Enter your choice (1-4): ")

        if choice == "1":
            print("Starting Button State Test...")
            while True:
                read_button_state_debug()
                time.sleep(0.5)
        elif choice == "2":
            test_neopixel()
        elif choice == "3":
            test_encoder()
        elif choice == "4":
            print("Exiting... Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")
except KeyboardInterrupt:
    print("\nTest interrupted. Exiting...")

