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
import numpy as np

class prog_Basic:
    
    mysynths = []
    # Sound properties
    def __init__(self, tube_count, led_per_tube):
        ROOT_FREQ = 220
        SCALE = [0, 2, 3, 5, 7, 8, 10, 12]  # natural minor
        FREQS = [ROOT_FREQ if n == 0
                 else int(round(ROOT_FREQ * (2**(1./12))**n))  # Note is equal to (root note * (2^12)^(semitone steps from root note) )
                 for n in SCALE]
        self.base_colours = np.tile(np.array(lighttools.sinebow(led_per_tube)), (tube_count, 1, 1)) # Default colour for each pixel
        self.base_colours /= 2
        self.current_colours = self.base_colours.copy()
        self.mysynths = []
        self.tubelength = led_per_tube
        for s in range(tube_count):
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