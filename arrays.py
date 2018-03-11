#
# Lite harp controller
# Jim Bluemel 2018
#

from __future__ import print_function

import numpy as np
import sc
import neopixel, lighttools, lidars, synths, programs
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
TUBE_LENGTH     = 1170  # mm
LED_PER_TUBE    = 70     # Number of LED strip per strip

PIXEL_COUNT = TUBE_COUNT * LED_PER_TUBE
PIXELS_PER_MM = LED_PER_TUBE/float(TUBE_LENGTH)

# Constraints
MIN_DIST = 300 # Sensor limitations
MAX_DIST = 1170 # Physical limitations

VOLUME = 0.5 # Passed to scsynth, 0 -> 1

# INIT

# Sensor setup
DEVSTRINGS = ["/dev/ttyUSB" + str(i) for i in range(TUBE_COUNT)] # ttyUSB0 --> ttyUSBn
lidars.init(DEVSTRINGS)

# LED strip setup
print("Seting up LED strip with %d LEDs" %PIXEL_COUNT)
strip = neopixel.Adafruit_NeoPixel(PIXEL_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

def np_array_to_colour(array):
    '''
    Takes a 3-element numpy array and returns a 24-bit colour as a zero-padded 32-bit int
    '''
    #array = array.clip(0, 255, out=array).astype(np.uint8) # Fix colours outside range. This limits rather than wrapping
    #return(array[0] << 16 | array[1] << 8 | array[2])
    colour = lighttools.LED_GAMMA[array[0]] << 16 | lighttools.LED_GAMMA[array[1]] << 8 | lighttools.LED_GAMMA[array[2]]
    return colour

def updatepixels(colours):
    pixels = colours.reshape(-1, 3) # Flatten
    #print(pixels)
    for i, pixel in enumerate(pixels):
        strip.setPixelColor(i, np_array_to_colour(pixel))
    strip.show()

# Supercolider setup
sc.start( verbose=1, spew=1)

# Find and initialize all the classes in the programs module
print("Initializing programs")
myprograms = [program(TUBE_COUNT, LED_PER_TUBE) 
            for name, program in inspect.getmembers(programs) 
            if inspect.isclass(program)
            and name[:5] == "test_"]
program_cycle = itertools.cycle(myprograms) # Loop through them forever
current_program = next(program_cycle)

# Ask the program for first frame
print("Set initial colours:")
frame = current_program.update([0,0,0,0,0,0,0,0])
updatepixels(frame)
this_time = time.time()
while True:
    # Check fur button press
    if not GPIO.input(26):
        # Button pressed
        current_program = next(program_cycle)
        frame = current_program.update([0,0,0,0,0,0,0,0])
        updatepixels(frame)
        time.sleep(0.5) # We could debounce the button press or we could just wait...  	
    
    # Main logic
    distances = []
    last_time = this_time
    this_time = time.time()
    print("Loop ms: %f" % ((this_time - last_time) * 1000))    
    for tube in range(TUBE_COUNT):
        t0 = time.time()
        distance = lidars.get_distance(tube) # Get distance in mm        

        if MIN_DIST < distance < MAX_DIST:
            pixel_dist = int(distance * PIXELS_PER_MM)
        else:
            pixel_dist = 0            
        distances.append(pixel_dist)
        t1 = time.time()
        print("Lidar time: %f Distance: %d" % (t1 - t0, distance))        
    t0 = time.time()
    t0 = time.time()
    frame = current_program.update(distances)
    t1 = time.time()
    print("Program time: ", t1 - t0)
    t0 = time.time()    
    updatepixels(frame)
    t1 = time.time()
    print("Pixel time: ", t1 - t0)
    #print(time.time() * 1000)
    time.sleep(0.001)
    
