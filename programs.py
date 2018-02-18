#
# Prototype program
# Programs must implement:
# - Vars:
#       notes: python list of 8 frequencies in hz for the notes; low to high
#       base_colours: np array of starting colours for the pixels
# 
# - Methods:
#       update(distances)
#       end
import synths, lighttools
import random
import numpy as np

class prog_Basic:
    
    mysynths = []
    # Sound properties
    def __init__(self, tube_count, led_per_tube):
        self.tubelength = led_per_tube
        FREQS = [220, 247, 262, 294, 330, 349, 392, 440]
        self.base_colours = np.tile(np.array(lighttools.sinebow(led_per_tube)), (tube_count, 1, 1)) # Default colour for each pixel
        self.base_colours /= 2 # Soften the colours a bit.
        self.current_colours = self.base_colours.copy() # Initial colours match base colours
        self.mysynths = []
        
        for s in range(tube_count):
            # Add a synth for each tube at the correct freq
            self.mysynths.append(synths.syn_Moog(FREQS[s]))
    
    def update(self, distances):
        # Decay
        self.current_colours = lighttools.fade(self.current_colours, self.base_colours, 10)
        
        for tube, distance in enumerate(distances):
            controller = self.mysynths[tube]
            if distance > 0:           
                # Update pixels
                #
                # Light up the pixel at the detected position
                self.current_colours[tube, distance] = lighttools.WHITE #255 - base_colours[tube, pixel_dist]
                # And a couple either side for extra brightness
                for i in range(2):
                        self.current_colours[tube, min(distance + i, self.tubelength - 1)] = lighttools.WHITE #255 - base_colours[tube, pixel_dist]
                        self.current_colours[tube, max(distance - i, 0)] = lighttools.WHITE #255 - base_colours[tube, pixel_dist]
                
                # Update synths
                #
                # Set modulation and ensure sound playing
                controller.modulate(distance)
                if not controller.playing:
                    controller.start()
            else:
                if controller.playing:
                    controller.stop()                
        return self.current_colours
        
class prog_Fire:
    
    mysynths = []
    # Sound properties
    def __init__(self, tube_count, led_per_tube):
        self.tube_length = led_per_tube
        self.tube_count = tube_count
        ROOT_FREQ = 220
        SCALE = [0, 2, 3, 5, 7, 8, 10, 12]  # natural minor
        FREQS = [ROOT_FREQ if n == 0
                 else int(round(ROOT_FREQ * (2**(1./12))**n))  # Note is equal to (root note * (2^12)^(semitone steps from root note) )
                 for n in SCALE]
        # current_colours = np.tile(lighttools.BLACK, (TUBE_COUNT, LED_PER_TUBE, 1)) # col, row, rgb
        self.base_colours = np.tile(np.array(lighttools.RED), (tube_count, led_per_tube, 1)) # Default colour for each pixel
        self.base_colours /= 2 # Soften the colours a bit.
        self.current_colours = self.base_colours.copy() # Initial colours match base colours
        self.mysynths = []
        
        for s in range(tube_count):
            # Add a synth for each tube at the correct freq
            self.mysynths.append(synths.syn_Moog(FREQS[s]))
    
    def update(self, distances):
        
        r = 255
        g = 15
        b = 12
        
        for tube, distance in enumerate(distances):
            for pixel in range(self.tube_length):
                flicker = random.randint(0, 60)
                r1 = r - flicker
                g1 = g + flicker
                b1 = max(g - flicker, 0)
                self.current_colours[tube, pixel] = np.array([g1, r1, b1])       
            
            controller = self.mysynths[tube]
            if distance > 0:           
                # Update pixels
                #
                # Light up the pixel at the detected position
                self.current_colours[tube, distance] = lighttools.WHITE #255 - base_colours[tube, pixel_dist]
                # And a couple either side for extra brightness
                for i in range(2):
                        self.current_colours[tube, min(distance + i, self.tube_length - 1)] = lighttools.WHITE #255 - base_colours[tube, pixel_dist]
                        self.current_colours[tube, max(distance - i, 0)] = lighttools.WHITE #255 - base_colours[tube, pixel_dist]
                
                # Update synths
                #
                # Set modulation and ensure sound playing
                controller.modulate(distance)
                if not controller.playing:
                    controller.start()
            else:
                if controller.playing:
                    controller.stop()                
        return self.current_colours