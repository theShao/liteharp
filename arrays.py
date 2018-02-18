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
'''
# Sound properties
ROOT_FREQ = 220
SCALE = [0, 2, 3, 5, 7, 8, 10, 12]  # natural minor
FREQS = [ROOT_FREQ if n == 0
         else int(round(ROOT_FREQ * (2**(1./12))**n))  # Note is equal to (root note * (2^12)^(semitone steps from root note) )
         for n in SCALE]
'''
VOLUME = 0.5 # Passed to scsynth, 0 -> 1


# Pixel arrays
current_colours = np.tile(lighttools.BLACK, (TUBE_COUNT, LED_PER_TUBE, 1)) # col, row, rgb
base_colours = np.tile(np.array(lighttools.sinebow(LED_PER_TUBE)), (TUBE_COUNT, 1, 1)) # Default colour for each pixel

# INIT

# Sensor setup
DEVSTRINGS = ["/dev/ttyUSB" + str(i) for i in range(TUBE_COUNT)] # ttyUSB0 --> ttyUSBn
lidars.init(DEVSTRINGS)

# LED strip setup
print("Seting up LED strip with %d LEDs" %PIXEL_COUNT)
strip = neopixel.Adafruit_NeoPixel(PIXEL_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

# Supercolider setup
sc.start( verbose=1, spew=1)

# Program initialisation

myprograms = []
myprograms.append(programs.prog_Basic(TUBE_COUNT, LED_PER_TUBE))

current_colours = myprograms[0].update([0,0,0,0,0,0,0,0])

print("Program started")
    
def updatepixels(colours):
    pixels = current_colours.reshape(-1, 3) # Flatten
    #print(pixels)
    for i, pixel in enumerate(pixels):
        strip.setPixelColor(i, lighttools.np_array_to_colour(pixel))
    strip.show()

#base_colours /= 2
#current_colours = base_colours.copy()
print("Setting startup colours:")
print(current_colours)
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
    time.sleep(0.01)
    '''
    # Decay
    current_colours = lighttools.fade(current_colours, base_colours, 10)    
    
    for tube in range(TUBE_COUNT):        
        distance = lidars.get_distance(tube) # Get distance in mm
        #distance -= 90 # sensor correction
        #print("Tube: %d Dist: %d"  %(tube, distance))

        controller = mysynths[tube]

        if MIN_DIST < distance < MAX_DIST:
            pixel_dist = int(distance * PIXELS_PER_MM)

            # Light up the pixel at the detected position
            current_colours[tube, pixel_dist] = lighttools.WHITE #255 - base_colours[tube, pixel_dist]
            # And a couple either side for extra brightness
            for i in range(2):
                    current_colours[tube, min(pixel_dist + i, LED_PER_TUBE - 1)] = lighttools.WHITE #255 - base_colours[tube, pixel_dist]
                    current_colours[tube, max(pixel_dist - i, 0)] = lighttools.WHITE #255 - base_colours[tube, pixel_dist]
            
            # Set modulation and ensure sound playing
            controller.modulate(distance) # Modulate the synth that's currently playing
            if not controller.playing:
                controller.start()
        else:
            if controller.playing:
                controller.stop()
    updatepixels(current_colours)
    time.sleep(0.01)
    '''        
        
"""
while True:
    for i in range(PIXEL_COUNT - 1):
        # Decay
        difs = base_colours - current_colours
        change = difs * decay
        current_colours += change        
        
        # Switch a pixel
        current_colours[0, i] = 255 - current_colours[0, i]
        '''
        # precay a few in front
        for j in range(10):
            precay_pixel = i + j
            if precay_pixel >= PIXEL_COUNT:
                break
            else:
                current_colours[0, i] = 255 - current_colours[0, i]
        '''
        '''
        for j in range(chasers):
            pos = i + (PIXEL_COUNT / chasers) * j
            #print pos
            while pos >= PIXEL_COUNT:
                pos = PIXEL_COUNT - (pos - PIXEL_COUNT) - 1
            while pos < 0:
                pos = 0
            #print pos
            current_colours[0, pos] = 255 - current_colours[0, pos] # Opposite colour
        '''
        updatepixels()
        time.sleep(0.05) 
        
    for i in range(PIXEL_COUNT - 1, 0, -1):
        # Decay
        difs = base_colours - current_colours
        change = difs * decay
        current_colours += change
        
        # Switch a pixel
        current_colours[0, i] = 255 - current_colours[0, i]
        updatepixels()
        time.sleep(0.05)        
"""