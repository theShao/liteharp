import neopixel, lighttools, time, random
import numpy as np

# LED STRIP
LED_PIN         = 13      # GPIO pin connected to the strip (must support PWM!).
LED_CHANNEL    = 1       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_FREQ_HZ     = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA         = 10      # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS  = 255      # Set to 0 for darkest and 255 for brightest
LED_INVERT      = False   # True to invert the signal (when using NPN transistor level shift)

TUBE_COUNT = 8
LED_PER_TUBE = 70


PIXEL_COUNT = TUBE_COUNT * LED_PER_TUBE

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

palette = np.genfromtxt('blackbodyGRB.csv', delimiter=',', dtype=None)
print(palette)
COOLING = 35
SPARKING = 120
heat = [[0 for i in range(LED_PER_TUBE)] for j in range(TUBE_COUNT)]
print(heat)
colours = np.tile([0,0,0], (TUBE_COUNT, LED_PER_TUBE, 1))
print(colours)

while True:
    for tube in range(TUBE_COUNT):
        # Translated from code at https://github.com/FastLED/FastLED/blob/master/examples/Fire2012/Fire2012.ino
        # Cool down each cell
        for i, temp in enumerate(heat[tube]):
            heat[tube][i] = max(int(heat[tube][i] - random.randint(0, ((COOLING * 10)/ LED_PER_TUBE) + 2)), 0)
        # Drift heat upwards and diffuse with surrounding pixels
        for k in range(LED_PER_TUBE - 1, 2, -1):
            heat[tube][k] = int((heat[tube][k - 1] + heat[tube][k - 2] + heat[tube][k - 2])/3)
        # Generate new spark near the bottom
        if (random.randint(0, 255) < SPARKING):
            y = random.randint(0, 7)
            heat[tube][y] = min(heat[tube][y] + random.randint(160, 255), 255)
        # Map heats to colours
        for i, temp in enumerate(heat[tube]):
            temp = int(temp * 240.0/255) # Avoid the top end
            colour = palette[temp]
            colours[tube][i] = colour    
    updatepixels(colours)
    time.sleep(0.01) 