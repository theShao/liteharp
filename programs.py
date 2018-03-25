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

class tube(object):
    pass

'''
class test_Rainbow:
    mysynths = []
    # Sound properties
    def __init__(self, tube_count, led_per_tube):
        self.tubelength = led_per_tube
        #self.base_colours = np.tile(np.array(lighttools.BLUE), (tube_count, led_per_tube, 1)) #.astype(np.uint8) # Default colour for each pixel        
        self.base_colours = np.tile(np.array(lighttools.sinebow(led_per_tube, 180)), (tube_count, 1, 1)) #.astype(np.uint8) # Default colour for each pixel        
        #self.base_colours /= 2 # Soften the colours a bit.
        self.current_colours = self.base_colours.copy() # Initial colours match base colours
        self.mysynths = []
        
        notes = [45, 47, 48, 50, 52, 53, 56, 57]
        for s in range(tube_count):
            # Add a synth for each tube at the correct freq
            self.mysynths.append(synths.syn_Midi(s, notes[s] + 12))
    
    def update(self, distances):
        # Decay
        self.current_colours = lighttools.fade(self.current_colours, self.base_colours, 10)
        for tube, distance in enumerate(distances):
            controller = self.mysynths[tube]
            if distance > 0:
                
                # Update synths
                #
                # Set modulation and ensure sound playing
                controller.modulate(min(distance * 2, 127))
                if not controller.playing:
                    controller.start()            
                
                # Update pixels
                #
                # Account for dead pixels. TODO
                distance += 12
                # Light up 5 pixels at the detected position
                self.current_colours[tube, distance-2:distance+2] = lighttools.WHITE #255 - base_colours[tube, pixel_dist]

            else:
                if controller.playing:
                    controller.stop()
        return self.current_colours
'''

'''        
class test_Stackbars:    
   
    # Sound properties
    def __init__(self, tube_count, led_per_tube):
        self.tubelength = led_per_tube
        self.tube_count = tube_count
        self.mysynths = []
        
        blue = np.array([88, 114, 232])
        white = np.array([255, 255, 255])
        black = np.array([0, 0, 0])
        self.fore_colours = np.tile(lighttools.make_fade(blue, white, led_per_tube), (tube_count, 1, 1))
        self.back_colours = np.tile(black, (tube_count, led_per_tube, 1))
        self.current_colours = self.back_colours.copy()
        
        self.auto_tube = 0
        self.auto_pixel = 0
        
        notes = [45, 47, 48, 50, 52, 53, 56, 57]
        for s in range(tube_count):
            # Add a synth for each tube at the correct freq
            self.mysynths.append(synths.syn_Midi(s, notes[s] + 12))
    
    def update(self, distances):
        if sum(distances) == 0:
            # Automatic mode.
            # Decay
            self.current_colours = lighttools.fade(self.current_colours, self.back_colours, 10)
            self.current_colours[self.auto_tube, self.auto_pixel] = self.fore_colours[self.auto_tube, self.auto_pixel]
            self.auto_pixel += 1
            if self.auto_pixel >= self.tubelength:
                self.auto_pixel = 0
                self.auto_tube = random.randint(0, self.tube_count)
            distances[self.auto_tube] = self.auto_pixel
            
        for tube, distance in enumerate(distances):
            controller = self.mysynths[tube]
            if distance > 0:                
                # Update synths
                #
                # Set modulation and ensure sound playing
                controller.modulate(min(distance * 2, 127))
                if not controller.playing:
                    controller.start()            

            else:
                if controller.playing:
                    controller.stop()
            
            # Account for dead pixels. TODO
            distance += 12
            # Set all pixels below hand to foreground colours
            self.current_colours[tube] = np.concatenate((self.fore_colours[tube, :distance], self.back_colours[tube, distance:]))

        return self.current_colours
'''
'''

class test_Rippler:    
   
    # Sound properties
    def __init__(self, tube_count, led_per_tube):
        self.tube_length = led_per_tube
        self.tube_count = tube_count
        self.midi_ratio = 127/led_per_tube
        self.synths = []
        
        blue = np.array([88, 60, 232])
        turq = np.array([234, 40, 214])
        white = np.array([255, 255, 255])
        black = np.array([0, 0, 0])
        column = np.concatenate((lighttools.make_fade(blue, turq, led_per_tube/2), lighttools.make_fade(turq, blue, led_per_tube/2)), axis=0)
        factor = int(led_per_tube/tube_count)
        self.current_colours = np.array([np.roll(column, t, axis=0) for t in range(tube_count)])
        self.base_colours = self.current_colours.copy()
        notes = [45, 47, 48, 50, 52, 53, 56, 57]
        for s in range(tube_count):        
            # Add a synth for each tube at the correct freq
            self.synths.append(synths.syn_Midi(s, notes[s] + 12))
        self.auto_ticks = [random.randint(0, 9) for _ in range(tube_count)]
        self.auto_directions = [random.choice([-1, 1]) for _ in range(tube_count)]
        self.auto_bubbles = [[0, 0] for _ in range(tube_count)]
        self.auto_play = True
        self.idle_count = 0        
        
    def update(self, distances):        
        if distances == [0] * self.tube_count:
            self.idle_count += 1
            if self.idle_count >= 100:
                self.auto_play = True
                self.idle_count = 0
        else:
            self.auto_bubbles = [[0, 0] for _ in range(self.tube_count)]
            self.idle_count = 0
            self.auto_play = False
            
        for tube, distance in enumerate(distances):
            controller = self.synths[tube]
            #
            # Update the timer
            #
            self.auto_ticks[tube] += 1
            if self.auto_ticks[tube] > 100:
                self.auto_ticks[tube] = 1
            
            #
            # Update the background
            #            
            if self.auto_ticks[tube] % 10 == 0:
                # Maybe change direction of background
                self.auto_directions[tube] = random.choice([-1, 1])
                self.auto_ticks[tube] = 0
            
            if self.auto_ticks[tube] % 1 == 0:                
                # Fade from the previous frame to where the background was for previous frame
                self.current_colours[tube] = lighttools.fade(self.current_colours[tube], self.base_colours[tube], 5)
                # Roll the background pixels for reference
                self.base_colours[tube] = np.roll(self.base_colours[tube], self.auto_directions[tube], axis=0)
                # Roll all pixels one place
                self.current_colours[tube] = np.roll(self.current_colours[tube], self.auto_directions[tube], axis=0)
                     
            
            if self.auto_play:
                # Run bubbles if present
                # bubble: list[position, speed]
                if self.auto_bubbles[tube][0] > 0:                    
                    # Move the bubble up the tube
                    self.auto_bubbles[tube][0] += self.auto_bubbles[tube][1]

                    # Check if we've reached the top of the tube
                    if self.auto_bubbles[tube][0] >= self.tube_length:
                        self.auto_bubbles[tube][0] = 0
                    else:
                        # Fake the distance reading
                        distance = self.auto_bubbles[tube][0]
                else:
                    # Maybe make a new bubble
                    if random.randint(0, 1000) == 0:
                        self.auto_bubbles[tube] = [1, random.randint(1, 3)]     
            
            if distance > 0:                
                # Update synths
                #
                # Set modulation and ensure sound playing
                controller.modulate(int(min(distance * self.midi_ratio, 127)))
                if not controller.playing:
                    controller.start()                 

                # Track distance with pixels
                self.current_colours[tube, distance] = np.array([255, 255, 255])
                
            else:
                # Stop the synth
                if controller.playing:
                    controller.stop()

        return self.current_colours

'''
        
        
class test_Fire:    
    blackbody_palette = [[0,0,0],[35,15,9],[60,22,17],[88,27,22],[117,30,26],[148,32,31],[177,38,35],[193,65,29],
                        [209,88,20],[223,113,5],[226,141,4],[228,169,3],[229,195,5],[235,218,74],[249,236,168],[255,255,255]]
    # Sound properties
    def __init__(self, tube_count, led_per_tube):
        self.tube_length = led_per_tube
        self.tube_count = tube_count
        self.midi_ratio = 127.0/led_per_tube
        black = np.array([0, 0, 0])
        self.synths = []        
        self.current_colours = np.tile(black, (tube_count, led_per_tube, 1))
        self.base_colours = self.current_colours.copy()
        self.auto_play = True
        self.idle_count = 0
        notes = [i - 12 for i in [45, 47, 48, 50, 52, 53, 56, 57]]
        for s in range(tube_count):        
            # Add a synth for each tube at the correct freq
            self.synths.append(synths.syn_Midi(s, notes[s] + 12))
        
        self.palette = np.genfromtxt('blackbodyGRB.csv', delimiter=',', dtype=None)
        self.COOLING = 55
        self.SPARKING = 75
        self.heat = [[0 for i in range(led_per_tube)] for j in range(tube_count)]
        
        
    def update(self, distances):        
        '''
        if distances == [0] * self.tube_count:
            self.idle_count += 1
            if self.idle_count >= 100:
                self.auto_play = True
                self.idle_count = 0
        else:
            self.idle_count = 0
            self.auto_play = False
        '''   
        for tube, distance in enumerate(distances):
            controller = self.synths[tube]
            
            # Cool down each cell
            for i, temp in enumerate(self.heat[tube]):
                self.heat[tube][i] = max(int(self.heat[tube][i] - random.randint(0, ((self.COOLING * 10)/ self.tube_length) + 2)), 0)
            # Drift heat upwards and diffuse with surrounding pixels
            for k in range(self.tube_length - 1, 2, -1):
                self.heat[tube][k] = int((self.heat[tube][k - 1] + self.heat[tube][k - 2] + self.heat[tube][k - 2])/3)
            '''    
            if self.auto_play:
                # Generate new spark near the bottom
                if (random.randint(0, 255) < self.SPARKING):
                    y = random.randint(0, 7)
                    self.heat[tube][y] = min(self.heat[tube][y] + random.randint(160, 255), 255)
            else:
                # Generate a new spark at detected position
                self.heat[tube][distance] = min(self.heat[tube][distance] + random.randint(160, 255), 255)
                # Set all pixels below to high temperature
                self.heat[tube][:distance] = [min(self.heat[tube][i] + random.randint(160, 255), 255) for i in range(distance)]
            '''          
            
            if distance > 0:                
                # Update synths
                #
                # Set modulation and ensure sound playing
                controller.modulate(int(min(distance * self.midi_ratio, 127)))
                if not controller.playing:
                    controller.start()                
                
                # Generate a new spark at detected position
                self.heat[tube][distance] = min(self.heat[tube][distance] + random.randint(160, 255), 255)
                # Set all pixels below to high temperature
                self.heat[tube][:distance] = [min(self.heat[tube][i] + random.randint(160, 255), 255) for i in range(distance)]
                
            else:
                # Stop the synth
                if controller.playing:
                    controller.stop()
                
                # Generate new spark near the bottom
                if (random.randint(0, 255) < self.SPARKING):
                    y = random.randint(0, 7)
                    self.heat[tube][y] = min(self.heat[tube][y] + random.randint(50, 150), 255)
            
            # Map heats to colours
            for i, temp in enumerate(self.heat[tube]):
                temp = int(temp * 240.0/255) # Avoid the top end
                colour = self.palette[temp]
                self.current_colours[tube][i] = colour      
        
        return self.current_colours
       
       
class prog_Basic:
    
    mysynths = []
    # Sound properties
    def __init__(self, tube_count, led_per_tube):
        self.tubelength = led_per_tube
        FREQS = [220, 247, 262, 294, 330, 349, 392, 440]
        self.base_colours = np.tile(np.array(lighttools.sinebow(led_per_tube, 200)), (tube_count, 1, 1)) # Default colour for each pixel
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