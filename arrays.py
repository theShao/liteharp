from __future__ import print_function

import numpy as np
import sc
import neopixel, lighttools, lidars, synths, programs
import time

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
strip = neopixel.Adafruit_NeoPixel(PIXEL_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL))
strip.begin()

def updatepixels(colours):
    pixels = colours.reshape(-1, 3) # Flatten
    #print(pixels)
    for i, pixel in enumerate(pixels):
        strip.setPixelColor(i, lighttools.np_array_to_colour(pixel))
    strip.show()

# Supercolider setup
sc.start( verbose=1, spew=0)

# Program initialisation
print("Initialising Programs")
myprograms = []
myprograms.append(programs.prog_Fire(TUBE_COUNT, LED_PER_TUBE))

# Get initial colours (same as colours when nothing detected)
print("Setting startup colours:")
current_colours = myprograms[0].update([0,0,0,0,0,0,0,0])
updatepixels(current_colours)

while True:
    distances = []
    for tube in range(TUBE_COUNT):        
        distance = lidars.get_distance(tube) # Get distance in mm
        if MIN_DIST < distance < MAX_DIST:
            pixel_dist = int(distance * PIXELS_PER_MM)
        else:
            pixel_dist = 0
        distances.append(pixel_dist)
    current_colours = myprograms[0].update(distances)
    updatepixels(current_colours)
    time.sleep(0.002)
