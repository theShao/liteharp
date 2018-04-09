"""
Functions for controlling a strip of neopixels
Jim, 29/04/2015
Some functions taken from the ws281x library.
TODO: Either modify neopixels.py or make this a complete wrapper for it
"""

# Frame Rate = 800000 / 24 / Number of LEDs

from neopixel import Color
import numpy as np
import random

REVERSED = True

# Colours
GREEN = [255, 0, 0]
RED = [0, 255, 0]
BLUE = [0, 0, 255]
WHITE = [255, 255, 255]
BLACK = [0, 0, 0]


LED_GAMMA = [
0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2,
2, 2, 2, 3, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5,
6, 6, 6, 7, 7, 7, 8, 8, 8, 9, 9, 9, 10, 10, 11, 11,
11, 12, 12, 13, 13, 13, 14, 14, 15, 15, 16, 16, 17, 17, 18, 18,
19, 19, 20, 21, 21, 22, 22, 23, 23, 24, 25, 25, 26, 27, 27, 28,
29, 29, 30, 31, 31, 32, 33, 34, 34, 35, 36, 37, 37, 38, 39, 40,
40, 41, 42, 43, 44, 45, 46, 46, 47, 48, 49, 50, 51, 52, 53, 54,
55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70,
71, 72, 73, 74, 76, 77, 78, 79, 80, 81, 83, 84, 85, 86, 88, 89,
90, 91, 93, 94, 95, 96, 98, 99,100,102,103,104,106,107,109,110,
111,113,114,116,117,119,120,121,123,124,126,128,129,131,132,134,
135,137,138,140,142,143,145,146,148,150,151,153,155,157,158,160,
162,163,165,167,169,170,172,174,176,178,179,181,183,185,187,189,
191,193,194,196,198,200,202,204,206,208,210,212,214,216,218,220,
222,224,227,229,231,233,235,237,239,241,244,246,248,250,252,255]


def wheel(position, n = 255):
    """Generate rainbow colors across n positions. Returns (R, G, B) tuple"""
    position *= int(255/n) # Scale input to the 0-255 range    
    #p = position * 3 * r
    if position < 85:
        return Color(position*3, 255 - position*3, 0)
    elif position < 170:
        position -= 85
        return Color(255 - position*3, 0, position*3)
    else:
        position -= 170
        return Color(0, position*3, 255 - position*3)

def wheel_RGB(position, n = 255):
    """Generate rainbow colors across n positions. Returns (R, G, B) tuple"""
    position *= int(255/n) # Scale input to the 0-255 range    
    #p = position * 3 * r
    if position < 85:
        return np.array([position*3, 255 - position*3, 0])
    elif position < 170:
        position -= 85
        return np.array([255 - position*3, 0, position*3])
    else:
        position -= 170
        return np.array([0, position*3, 255 - position*3])

def sinebow(count = 100, brightness = 255):
    out = []
    step = 1./count
    for i in np.arange(0.0, 1.0, step):
        i += 0.5
        i *= -1
        g = np.sin(np.pi * i)
        r = np.sin(np.pi * (i + 1./3))
        b = np.sin(np.pi * (i + 2./3))        
        out.append([int(brightness*chan**2) for chan in (r, g, b)])
    return(out)

def whitelight(strip, mags):
    for i in range(len(strip.numPixels())):
        strip.setPixelColor(i, Color(mags[i], mags[i], mags[i]))
    strip.show()

def clear(strip):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, BLACK)
    strip.show()

def arrayToColour(array):
    #Turns a 3-element array into a neopixel Color
    # Input should be scaled to 0-255
    r, g, b = int(array[0]), int(array[1]), int(array[2])
    return Color(r, g, b)

def np_array_to_colour(array, gamma_correct = True):
    '''
    Takes a 3-element numpy array and returns a 24-bit colour as a zero-padded 32-bit int
    '''
    #array = array.clip(0, 255, out=array).astype(np.uint8) # Fix colours outside range. This limits rather than wrapping
    #return(array[0] << 16 | array[1] << 8 | array[2])
    if gamma_correct:
        colour = LED_GAMMA[array[0]] << 16 | LED_GAMMA[array[1]] << 8 | LED_GAMMA[array[2]]
    else:
        return(array[0] << 16 | array[1] << 8 | array[2])
    return colour

def fade(colours, target_colours, rate = 1):
    '''
    Fade from one numpy array of pixel colours to another
    colours: 2-d numpy array of RGB values
    target_colours: 2-d numpy array of RGB values
    rate: number of steps over which to make the change
    Note that rate is relative; calling fade(x, y, 0.5) repeatedly will fade exponentially 
    '''
    diffs = target_colours - colours
    change = (diffs / rate) #.astype(np.uint8)
    return colours + change
    
def test(strip):
    rands = [[random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
             for pixel in range(strip.numPixels())]
    setpixels(strip, rands)

def setpixels(strip, colours, scale = False):
    # Convenience method that sets and updates the entire strip
    # Takes a list of integers that map directly to 24-bit colour space or a list of [r,g,b] ndarrays
     
    # Check whether we have more pixels or colours
    if len(colours) > strip.numPixels() :
        # Take colours until the strip's full.
        for i in range(strip.numPixels()):
            if REVERSED:
                n = strip.numPixels() - i
            else:
                n = i
            try: #Simplest case; we got a list of integers that map directly to 24-bit colour space
                strip.setPixelColor(n, colours[i])
            except: #We got a list of rgb arrays TODO: but what if we didn't??
                strip.setPixelColor(n, arrayToColour(colours[i]))
    else:
        scalefactor = int(strip.numPixels()/len(colours)) if scale else 1
        for i in range(len(colours)):
            for j in range(scalefactor):
                if REVERSED:
                    n = strip.numPixels() - (i*scalefactor + j)
                else:
                    n = i*scalefactor + j
                try:
                    strip.setPixelColor(n, colours[i])
                except:
                    strip.setPixelColor(n, arrayToColour(colours[i]))
    
    strip.show()

def make_fade(start_colour = np.array(RED), end_colour = np.array(BLUE), count = 70):
    colours = []
    diff = (end_colour - start_colour) / float(count - 1)
    for i in range(count):
        colours.append(start_colour)
        start_colour = np.add(start_colour, diff, casting='unsafe')
    return np.array(colours).astype(np.uint8)
    
def makeColorGradient(frequency1 = .2, frequency2 = .2, frequency3 = .2, phase1 = 0, phase2 = 2*np.pi/3, phase3 = 4*np.pi/3, center = 128, width = 127, len = 50):
    colours = []
    for i in range(len):    
        r = np.sin(frequency1*i + phase1) * width + center
        g = np.sin(frequency2*i + phase2) * width + center
        b = np.sin(frequency3*i + phase3) * width + center
        colours.append([int(r), int(g), int(b)])
    return colours

# Colour space conversion taken from https://stackoverflow.com/questions/27041559/rgb-to-hsv-python-change-hue-continuously
# See here for performance comparisons of various approaches:
# https://stackoverflow.com/questions/38055065/efficient-way-to-convert-image-stored-as-numpy-array-into-hsv
    
def rgb_to_hsv(rgb):
    # Translated from source of colorsys.rgb_to_hsv
    # r,g,b should be a numpy arrays with values between 0 and 255
    # rgb_to_hsv returns an array of floats between 0.0 and 1.0.
    rgb = rgb.astype('float')
    hsv = np.zeros_like(rgb)
    # in case an RGBA array was passed, just copy the A channel
    hsv[..., 3:] = rgb[..., 3:]
    r, g, b = rgb[..., 1], rgb[..., 0], rgb[..., 2]
    maxc = np.max(rgb[..., :3], axis=-1)
    minc = np.min(rgb[..., :3], axis=-1)
    hsv[..., 2] = maxc
    mask = maxc != minc
    hsv[mask, 1] = (maxc - minc)[mask] / maxc[mask]
    rc = np.zeros_like(r)
    gc = np.zeros_like(g)
    bc = np.zeros_like(b)
    rc[mask] = (maxc - r)[mask] / (maxc - minc)[mask]
    gc[mask] = (maxc - g)[mask] / (maxc - minc)[mask]
    bc[mask] = (maxc - b)[mask] / (maxc - minc)[mask]
    hsv[..., 0] = np.select(
        [r == maxc, g == maxc], [bc - gc, 2.0 + rc - bc], default=4.0 + gc - rc)
    hsv[..., 0] = (hsv[..., 0] / 6.0) % 1.0
    return hsv

def hsv_to_rgb(hsv):
    # Translated from source of colorsys.hsv_to_rgb
    # h,s should be a numpy arrays with values between 0.0 and 1.0
    # v should be a numpy array with values between 0.0 and 255.0
    # hsv_to_rgb returns an array of uints between 0 and 255.
    rgb = np.empty_like(hsv)
    rgb[..., 3:] = hsv[..., 3:]
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    i = (h * 6.0).astype('uint8')
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    i = i % 6
    conditions = [s == 0.0, i == 1, i == 2, i == 3, i == 4, i == 5]
    rgb[..., 1] = np.select(conditions, [v, q, p, p, t, v], default=v)
    rgb[..., 0] = np.select(conditions, [v, v, v, q, p, p], default=t)
    rgb[..., 2] = np.select(conditions, [v, p, t, v, v, q], default=p)
    return rgb.astype('uint8')

def hueChange(arr, hue):
    hsv = rgb_to_hsv(arr)
    hsv[..., 0] = hue
    rgb = hsv_to_rgb(hsv)
    return rgb