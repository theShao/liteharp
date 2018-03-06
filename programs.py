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

class test_Midi:
    mysynths = []
    # Sound properties
    def __init__(self, tube_count, led_per_tube):
        self.tubelength = led_per_tube        
        self.base_colours = np.tile(np.array(lighttools.sinebow(led_per_tube))/1.5, (tube_count, 1, 1)) # Default colour for each pixel
        #self.base_colours /= 2 # Soften the colours a bit.
        self.current_colours = self.base_colours.copy() # Initial colours match base colours
        self.mysynths = []
        
        for s in range(tube_count):
            # Add a synth for each tube at the correct freq
            self.mysynths.append(synths.syn_Midi(0, 60))
    
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

class prog_Basic:
    
    mysynths = []
    # Sound properties
    def __init__(self, tube_count, led_per_tube):
        self.tubelength = led_per_tube
        FREQS = [220, 247, 262, 294, 330, 349, 392, 440]
        self.base_colours = np.tile(np.array(lighttools.sinebow(led_per_tube))/1.5, (tube_count, 1, 1)) # Default colour for each pixel
        #self.base_colours /= 2 # Soften the colours a bit.
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
        
class prog_Sarah:
    #COLOURS = [[114, 238, 88], [151, 250, 119], [197, 250, 143], [223, 255, 210], [189, 217, 214], [195, 210, 254], [95, 132, 198], [67, 89, 168]]
    COLOURS = [[112, 241, 90], [151, 250, 119], [171, 250, 130], [210, 255, 145], [205, 240, 175], [199, 224, 200], [160, 216, 189], [148, 200, 161]]
    mysynths = []
    # Sound properties
    def __init__(self, tube_count, led_per_tube):
        self.tubelength = led_per_tube
        self.tube_count = tube_count
        ROOT_FREQ = 110
        SCALE = [0, 2, 3, 5, 7, 8, 11, 12]  # natural minor
        FREQS = [ROOT_FREQ if n == 0
                 else int(round(ROOT_FREQ * (2**(1./12))**n))  # Note is equal to (root note * (2^12)^(semitone steps from root note) )
                 for n in SCALE]
        # current_colours = np.tile(lighttools.BLACK, (TUBE_COUNT, LED_PER_TUBE, 1)) # col, row, rgb
        base_colours = []
        for tube in range(tube_count):
            colour =[prog_Sarah.COLOURS[tube]] * led_per_tube
            base_colours.append(colour)
        
        self.base_colours = np.array(base_colours) / 1.5
        self.current_colours = self.base_colours.copy() # Initial colours match base colours
        self.mysynths = []
        
        for s in range(tube_count):
            # Add a synth for each tube at the correct freq
            self.mysynths.append(synths.syn_Organdonor(FREQS[s]))
    
    def update(self, distances):
        self.current_colours = lighttools.fade(self.current_colours, self.base_colours, 10)

        for tube, distance in enumerate(distances):
            controller = self.mysynths[tube]
            if distance > 0:           
                # Update pixels
                #
                # Light up the pixel at the detected position
                self.current_colours[tube, distance] = [64, 87, 168] # lighttools.WHITE #255 - base_colours[tube, pixel_dist]
                # And a couple either side for extra brightness
                for i in range(2):
                        self.current_colours[tube, min(distance + i, self.tubelength - 1)] = [64, 87, 168] #lighttools.WHITE #255 - base_colours[tube, pixel_dist]
                        self.current_colours[tube, max(distance - i, 0)] = [64, 87, 168] # lighttools.WHITE #255 - base_colours[tube, pixel_dist]
                
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