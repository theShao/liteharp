import neopixel, lighttools, time, random
import numpy as np

# LED STRIP
LED_PIN         = 13      # GPIO pin connected to the strip (must support PWM!).
LED_CHANNEL    = 1       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_FREQ_HZ     = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA         = 10      # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS  = 255      # Set to 0 for darkest and 255 for brightest
LED_INVERT      = False   # True to invert the signal (when using NPN transistor level shift)

PIXEL_COUNT = 70 * 8

INDIGO_DARK = [88, 114, 232]

colour = INDIGO_DARK

# LED strip setup
print("Seting up LED strip with %d LEDs" %PIXEL_COUNT)
strip = neopixel.Adafruit_NeoPixel(PIXEL_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()
print("LED Strip running")

def updatepixels(colours):
    pixels = colours.reshape(-1, 3) # Flatten
    #print(pixels)
    for i, pixel in enumerate(pixels):
        strip.setPixelColor(i, lighttools.np_array_to_colour(pixel))
    strip.show()

while True:
    colours = []
    for pixel in range(PIXEL_COUNT):
        mod_colour = []
        for hue in colour:
            mod_colour.append(max(min(hue + random.randint(-20, 20), 255), 0))
        colours.append(mod_colour)
    colours = np.array(colours)
    updatepixels(colours)
    time.sleep(0.1)

