#!/usr/bin/python
#
# Lite harp controller
# Jim Bluemel 2018
#

from __future__ import print_function

import numpy as np
import neopixel, lighttools, lidars, programs
import threading, itertools, time, inspect
import RPi.GPIO as GPIO

# Push button on gnd and BCM pin 26
GPIO.setmode(GPIO.BCM)
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Set up the pin for the pushswitch

# LED STRIP
LED_PIN         = 13      # GPIO pin connected to the strip (must support PWM!).
LED_CHANNEL    = 1       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_FREQ_HZ     = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA         = 10      # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS  = 255      # Set to 0 for darkest and 255 for brightest
LED_INVERT      = False   # True to invert the signal (when using NPN transistor level shift)

# INSTRUMENT
TUBE_COUNT      = 8       # Number of strips
TUBE_LENGTH     = 1170  # Length of the LED strip, mm
#PIXELS_PER_MM   = 0.06 # 60 led per metre strips
PIXELS_PER_TUBE    = 70     # Number of LED strip per strip
INVERT_PIXELS   = True # Pixels numbered top to bottom
INVERT_SENSORS  = True # Sensors attached at top
SENSOR_OFFSET   = 250     # Distance from the sensor to the first LED

# Constraints
MIN_DIST = 250 # Sensor limitations
#MAX_DIST = 1360 # Physical limitations
VOLUME = 0.5 # Passed to scsynth, 0 -> 1

# Derived
PIXEL_COUNT = TUBE_COUNT * PIXELS_PER_TUBE
PIXELS_PER_MM = float(PIXELS_PER_TUBE) / TUBE_LENGTH
PIXEL_OFFSET = int((MIN_DIST - SENSOR_OFFSET) * PIXELS_PER_MM) # First pixel that's inside the sensor range
MAX_DIST = 1350 #TUBE_LENGTH + SENSOR_OFFSET tweaked based on real-world results.

# INIT

# Sensor setup
DEVSTRINGS = ["/dev/tty-U" + str(i) for i in range(TUBE_COUNT)] # ttyU0 --> ttyUn
lidars.init(DEVSTRINGS)

# LED strip setup
print("Seting up LED strip with %d LEDs" %PIXEL_COUNT)
strip = neopixel.Adafruit_NeoPixel(PIXEL_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()
print("LED Strip running")

def updatepixels(colours):
    if INVERT_PIXELS: # Pixels are physically indexed top to bottom
        if INVERT_SENSORS: # Sensors are located at the top
            colours = np.flip(colours, 1)
            colours = np.pad(colours, [(0, 0), (PIXEL_OFFSET, 0), (0, 0)], mode='constant')
        else: # Sensors are physically located at the bottom
            colours = np.flip(colours, 1)
            colours = np.pad(colours, [(0, 0), (0, PIXEL_OFFSET), (0, 0)], mode='constant')
    else: # Pixels are physically indexed bottom to top
        if INVERT_SENSORS:
            colours = np.pad(colours, [(0, 0), (0, PIXEL_OFFSET), (0, 0)], mode='constant')
        else:
            colours = np.pad(colours, [(0, 0), (PIXEL_OFFSET, 0), (0, 0)], mode='constant')
    
    pixels = colours.reshape(-1, 3) # Flatten
    
    for i, pixel in enumerate(pixels):
        strip.setPixelColor(i, lighttools.np_array_to_colour(pixel))
    strip.show()

    
# Find and initialize all the classes in the programs module that are "live"
print("Initializing programs")
myprograms = [program(TUBE_COUNT, PIXELS_PER_TUBE - PIXEL_OFFSET) 
            for name, program in inspect.getmembers(programs) 
            if inspect.isclass(program)
            and name[:5] == "live_"]
program_cycle = itertools.cycle(myprograms) # Loop through them forever
current_program = next(program_cycle)
current_program.load()

# Ask the program for first frame
print("Set initial colours:")
frame = current_program.update([0,0,0,0,0,0,0,0])
updatepixels(frame)

this_time = time.time()

while True:
    # Check fur button press
    if not GPIO.input(26):
        # Button pressed
        current_program.stop()
        current_program = next(program_cycle)
        current_program.load()
        frame = current_program.update([0,0,0,0,0,0,0,0])
        updatepixels(frame)
        time.sleep(0.5) # We could debounce the button press or we could just wait...  	
    
    # Main logic
    
    # Reset
    distances = []
    last_time = this_time
    this_time = time.time()
    #print("Loop ms: %f" % ((this_time - last_time) * 1000))    
    
    # Sensor work
    t0 = time.time()
    for tube in range(TUBE_COUNT):
        
        reading = lidars.get_reading(tube) # Get distance in mm        
        #print("Sensor: {} Distance: {} Strenght: {} Quality: {} Mode: {}".format(tube, *(reading)))
        distance = reading[0]
        if MIN_DIST < distance < MAX_DIST:
            pixel_dist = int((distance - SENSOR_OFFSET) * PIXELS_PER_MM)
            if INVERT_SENSORS:
                pixel_dist = (PIXELS_PER_TUBE - 1) - pixel_dist
            else:
                pixel_dist -= PIXEL_OFFSET
        else:
            pixel_dist = 0            
        distances.append(pixel_dist)
    t1 = time.time()
    #print("Lidar time: %f "% (t1 - t0))        
    
    # Program work
    t0 = time.time()
    frame = current_program.update(distances)
    t1 = time.time()
    #print("Program time: ", t1 - t0)
    
    # Neopixel work
    t0 = time.time()    
    updatepixels(frame)
    t1 = time.time()
    #print("Pixel time: ", t1 - t0)
    
    time.sleep(0.001)
    
