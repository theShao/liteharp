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

class template:
    
    def __init__(self, tube_count, led_per_tube):
        self.tube_length = led_per_tube
        self.tube_count = tube_count
        self.midi_ratio = 127.0/led_per_tube
        self.midi_program = 0
        self.midi_velocity = 112
        self.midi_modulation = 1
        notes = [i for i in [45, 47, 48, 50, 52, 53, 56, 57]]
        # synth(channel, program, note, velocity, modulation)
        self.synths = [synths.syn_Midi(n, self.midi_program, notes[n], self.midi_velocity, self.midi_modulation)
                        for n in range(self.tube_count)]
        self.tick = 0
    
    def load(self):
    
        # Set all pixels to black
        black = np.array([0, 0, 0])               
        self.current_colours = np.tile(black, (self.tube_count, self.tube_length, 1))
        
        # Load synth patch
        for synth in self.synths:
            synth.load_program()
        
    def update(self, distances):
        
        for tube, distance in enumerate(distances):
            controller = self.synths[tube]      
            
            if distance > 0:                
                # Update synths
                #
                # Set modulation and ensure sound playing
                controller.modulate(int(min(distance * self.midi_ratio, 127)))
                if not controller.playing:
                    controller.start()                
                
            else:
                # Stop the synth
                if controller.playing:
                    controller.stop()          
        return self.current_colours

class live_Bubbles:        
    # Sound properties
    def __init__(self, tube_count, led_per_tube):
        self.tube_length = led_per_tube
        self.tube_count = tube_count
        self.midi_ratio = 127/led_per_tube
        self.synths = []
        
        self.midi_program = 0
        self.midi_modulation = 1
        self.midi_velocity = 112
        self.colour_cycle_speed = 0

        notes = [45, 47, 48, 50, 52, 53, 56, 57]
        # synth(channel, program, note, velocity, modulation)
        self.synths = [synths.syn_Midi(n, self.midi_program, notes[n], self.midi_velocity, self.midi_modulation)
                        for n in range(self.tube_count)]  
       
    def load(self):
        self.auto_ticks = [random.randint(0, 9) for _ in range(self.tube_count)]
        self.auto_directions = [random.choice([-1, 1]) for _ in range(self.tube_count)]
        self.auto_bubbles = [[0, 0] for _ in range(self.tube_count)]
        self.auto_play = True
        self.idle_count = 0     
    
        blue = np.array([88, 60, 232])
        turq = np.array([234, 40, 214])
        white = np.array([255, 255, 255])
        black = np.array([0, 0, 0])
        column = np.concatenate((lighttools.make_fade(blue, turq, self.tube_length/2), lighttools.make_fade(turq, blue, self.tube_length/2)), axis=0)
        self.current_colours = np.array([np.roll(column, t, axis=0) for t in range(self.tube_count)])
        self.base_colours = self.current_colours.copy()
        for synth in self.synths:
            synth.load_program()
    
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

class live_Sparkles:    
    
    def __init__(self, tube_count, led_per_tube):
        self.tube_length = led_per_tube
        self.tube_count = tube_count
        self.midi_ratio = 127.0/led_per_tube
        self.midi_program = 1
        self.midi_velocity = 112
        self.midi_modulation = 1
        self.colours = [[112, 241, 90], [151, 250, 119], [171, 250, 130], [210, 255, 145], [205, 240, 175], [199, 224, 200], [160, 216, 189], [148, 200, 161]]
        self.circle_colour = np.array([255, 255, 255])
        self.circle_spacing = 9 # Min radius of previous circle before we add another
        notes = [i + 12 for i in [45, 47, 48, 50, 52, 53, 56, 57]]
        # synth(channel, program, note, velocity, modulation)
        self.synths = [synths.syn_Midi(n, self.midi_program, notes[n], self.midi_velocity, self.midi_modulation)
                        for n in range(self.tube_count)]
        self.tick = 0
    
    def load(self):
    
        self.base_colours = []
        for tube in range(self.tube_count):
            colour =[self.colours[tube]] * self.tube_length
            self.base_colours.append(colour)
        
        self.base_colours = np.tile([64, 87, 168], (self.tube_count, self.tube_length, 1)) #np.array(self.base_colours)
        self.current_colours = self.base_colours.copy() # Initial colours match base colours
        
        self.circles = []
        # Load synth patch
        for synth in self.synths:
            synth.load_program()
        
    def update(self, distances):
        self.tick += 1
        self.current_colours = lighttools.fade(self.current_colours, self.base_colours, 5) #self.base_colours.copy()
        
        for tube, distance in enumerate(distances):
            controller = self.synths[tube]      
            
            if distance > 0:            
                #Check whether we've already got circles on this tube
                #position = [tube, distance]
                col_matches = [circle for circle in self.circles if tube == circle[0]] # and circle[2] < 9]
                space_matches = []
                # Move any centred around the wrong position
                for circle in col_matches:
                    circle[1] = distance
                    # Check if this circle prevents us adding a new one
                    if circle[2] < self.circle_spacing:
                        space_matches.append(circle)
                if len(space_matches) < 1:                    
                    # Add a circle centered on detected position
                    self.circles.append([tube, distance, 0]) # x, y, radius
                # Update synths
                #
                # Set modulation and ensure sound playing
                controller.modulate(int(min(distance * self.midi_ratio, 127)))
                if not controller.playing:
                    controller.start()                
                
            else:
                # Remove all circles from this tube
                self.circles = [circle for circle in self.circles if not tube == circle[0]]
                # Stop the synth
                if controller.playing:
                    controller.stop()          
        for circle in self.circles:
            x, y, radius = circle
            #Fade the circle as it expands
            colour = self.circle_colour #* 1/radius if radius > 0 else self.circle_colour
            # Draw the circle
            self.current_colours[x, min(y + radius, self.tube_length - 1)] = colour
            self.current_colours[x, max(y - radius, 0)] = colour
            self.current_colours[min(x + radius/5, self.tube_count - 1), y] = colour
            self.current_colours[max(x - radius/5, 0), y] = colour
            #np.clip(self.current_colours, 0, 255, out=self.current_colours)
            if self.tick % 2 == 0:
                # Expand the circle
                radius += 1
                # Remove expired circles
                if radius > self.tube_length:
                    self.circles.remove(circle)
                else:
                    circle[2] = radius
        #print(self.circles)        
        return self.current_colours        
        
class live_Fire:    
    # Loop speed as of 31/03 ~15ms
    
    def __init__(self, tube_count, led_per_tube):
        self.tube_length = led_per_tube
        self.tube_count = tube_count
        self.midi_ratio = 127.0/led_per_tube
        self.palette = np.genfromtxt('blackbodyGRB.csv', delimiter=',', dtype=None) # Loads precomputed black body palette
        self.COOLING = 50 # How quickly cells cool as they rise, 0-255
        self.SPARKING = 80 # How often new heat sparks are producted, 0-255        
        self.colour_cycle_speed = 0
        self.midi_program = 2
        self.midi_velocity = 112
        self.midi_modulation = 1
        self.auto_play = True
        notes = [i for i in [45, 47, 49, 50, 52, 54, 56, 57]]
        # synth(channel, program, note, velocity, modulation)
        self.synths = [synths.syn_Midi(n, self.midi_program, notes[n], self.midi_velocity, self.midi_modulation)
                        for n in range(self.tube_count)]
        self.tick = 0
    
    def load(self):
    
        # Set all pixels to black
        black = np.array([0, 0, 0])               
        self.current_colours = np.tile(black, (self.tube_count, self.tube_length, 1))
        
        # Initialize heat cells
        self.heat = [[0 for i in range(self.tube_length)]
                    for j in range(self.tube_count)]
        
        # Load synth patch
        for synth in self.synths:
            synth.load_program()
        
    def update(self, distances):
        for tube, distance in enumerate(distances):
            controller = self.synths[tube]
            
            # Cool down each cell
            for i, temp in enumerate(self.heat[tube]):
                self.heat[tube][i] = max(int(self.heat[tube][i] - random.randint(0, ((self.COOLING * 10)/ self.tube_length) + 2)), 0)
            
            # Drift heat upwards and diffuse with surrounding pixels
            for k in range(self.tube_length - 1, 2, -1):
                self.heat[tube][k] = int((2 * self.heat[tube][k - 1] + 2 * self.heat[tube][k - 2] + 2 * self.heat[tube][k - 2]
                                            + self.heat[(tube + 1) % 8][k - 1] + self.heat[(tube - 1) % 8][k - 1]) /8)
            
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
                self.heat[tube][:distance] = [min(self.heat[tube][i] + random.randint(160, 255), 255)
                                                for i in range(distance)]
                
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
        
        if self.colour_cycle_speed > 0:
            self.tick += self.colour_cycle_speed
            if self.tick == 360:
                self.tick = 0
            # Cycle the colours of the palette
            # This costs ~3ms. Much cheaper than converting each pixel
            self.palette = lighttools.hueChange(self.palette, self.tick/360.)
            
        return self.current_colours

class live_Rainbow:
    mysynths = []
    # Sound properties
    def __init__(self, tube_count, led_per_tube):
        self.tubelength = led_per_tube
        #self.base_colours = np.tile(np.array(lighttools.BLUE), (tube_count, led_per_tube, 1)) #.astype(np.uint8) # Default colour for each pixel        
        self.base_colours = np.tile(np.array(lighttools.sinebow(led_per_tube, 180)), (tube_count, 1, 1)) #.astype(np.uint8) # Default colour for each pixel        
        #self.base_colours /= 2 # Soften the colours a bit.
        self.current_colours = self.base_colours.copy() # Initial colours match base colours
        self.mysynths = []
        self.midi_program = 3
        self.midi_modulation = 1
        self.midi_velocity = 112
        
        notes = [45, 47, 48, 50, 52, 53, 56, 57]
        # synth(channel, program, note, velocity, modulation)
        self.synths = [synths.syn_Midi(n, self.midi_program, notes[n+12], self.midi_velocity, self.midi_modulation)
                        for n in range(self.tube_count)]          

    def load(self):
        for synth in self.synths:
            synth.load_program()        
    
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
                # Light up 5 pixels at the detected position
                self.current_colours[tube, distance-2:distance+2] = lighttools.WHITE #255 - base_colours[tube, pixel_dist]

            else:
                if controller.playing:
                    controller.stop()
        return self.current_colours
      
class live_Art:    
    
    def __init__(self, tube_count, led_per_tube):
        self.tube_length = led_per_tube
        self.tube_count = tube_count
        self.midi_ratio = 127.0/led_per_tube
        self.midi_program = 4
        self.midi_velocity = 112
        self.midi_modulation = 1
        self.colours = [[112, 241, 90], [151, 250, 119], [171, 250, 130], [210, 255, 145],
                        [205, 240, 175], [199, 224, 200], [160, 216, 189], [148, 200, 161]]
        notes = [i for i in [45, 47, 48, 50, 52, 53, 56, 57]]
        # synth(channel, program, note, velocity, modulation)
        self.synths = [synths.syn_Midi(n, self.midi_program, notes[n], self.midi_velocity, self.midi_modulation)
                        for n in range(self.tube_count)]
        self.tick = 0
    
    def load(self):
    
        self.base_colours = []
        for tube in range(self.tube_count):
            colour =[self.colours[tube]] * self.tube_length
            self.base_colours.append(colour)
        
        self.base_colours = np.array(self.base_colours)
        self.current_colours = self.base_colours.copy() # Initial colours match base colours
        # Load synth patch
        for synth in self.synths:
            synth.load_program()
        
    def update(self, distances):
        
        self.current_colours = lighttools.fade(self.current_colours, self.base_colours, 10)
        
        for tube, distance in enumerate(distances):
            controller = self.synths[tube]      
            
            if distance > 0:
                # Light up 5 pixels at the detected position
                self.current_colours[tube, distance-2:distance+2] = [64, 87, 168]

                # Update synths
                #
                # Set modulation and ensure sound playing
                controller.modulate(int(min(distance * self.midi_ratio, 127)))
                if not controller.playing:
                    controller.start()                
                
            else:
                # Stop the synth
                if controller.playing:
                    controller.stop()          
        return self.current_colours        

class test_AAColourBlender:    
    
    def __init__(self, tube_count, led_per_tube):
        self.tube_length = led_per_tube
        self.tube_count = tube_count
        self.midi_ratio = 127.0/led_per_tube
        self.midi_program = 3
        self.midi_velocity = 112
        self.midi_modulation = 1
        
        self.colours = [[255, 0, 0], [0, 255, 0], [0, 0, 255], [127, 127, 0],
                        [127, 0, 127], [0, 127, 127], [80, 80, 80], [200, 200, 200]]

        notes = [i + 12 for i in [45, 47, 48, 50, 52, 53, 56, 57]]
        # synth(channel, program, note, velocity, modulation)
        self.synths = [synths.syn_Midi(n, self.midi_program, notes[n], self.midi_velocity, self.midi_modulation)
                        for n in range(self.tube_count)]
        self.tick = 0
    
    def load(self):    
       
        # Set all pixels to black
        black = np.array([0, 0, 0])               
        self.current_colours = np.tile(black, (self.tube_count, self.tube_length, 1))
        self.base_colours = self.current_colours.copy()
        # Initialize a grid for each tube
        self.grid = np.tile(0, (self.tube_count, self.tube_count, self.tube_length, 3))
        # Load synth patch
        for synth in self.synths:
            synth.load_program()
        
    def update(self, distances):
        self.current_colours = self.base_colours.copy()
        self.grid[:] = 0 # np.nan #np.zeros([self.tube_count, self.tube_count, self.tube_length, 3])
        for tube, distance in enumerate(distances):
            controller = self.synths[tube]      
            
            if distance > 0:            
                # Set colour for each pixel in this column up to distance, and in each other column at this height
                self.grid[tube, tube, :] = self.colours[tube]
                self.grid[tube, :, distance-2:distance+2] = self.colours[tube]
                
                # Update synths
                #
                # Set modulation and ensure sound playing
                controller.modulate(int(min(distance * self.midi_ratio, 127)))
                if not controller.playing:
                    controller.start()                
                
            else:
                
                # Stop the synth
                if controller.playing:
                    controller.stop()          
        
        self.current_colours = np.clip(np.sum(self.grid, axis = 0), 0, 255).astype(np.uint8)
        
        return self.current_colours             

class test_AAAColourBlender:    
    
    def __init__(self, tube_count, led_per_tube):
        self.tube_length = led_per_tube
        self.tube_count = tube_count
        self.midi_ratio = 127.0/led_per_tube
        self.midi_program = 3
        self.midi_velocity = 112
        self.midi_modulation = 1
        
        self.colours = np.array([[255, 0, 0], [0, 255, 0], [0, 0, 255], [127, 127, 0],
                        [127, 0, 127], [0, 127, 127], [80, 80, 80], [200, 200, 200]])

        notes = [i + 12 for i in [45, 47, 48, 50, 52, 53, 56, 57]]
        # synth(channel, program, note, velocity, modulation)
        self.synths = [synths.syn_Midi(n, self.midi_program, notes[n], self.midi_velocity, self.midi_modulation)
                        for n in range(self.tube_count)]
        self.tick = 0
    
    def load(self):    
       
        # Set all pixels to black
        black = np.array([0, 0, 0])               
        self.current_colours = np.tile(black, (self.tube_count, self.tube_length, 1))
        self.base_colours = self.current_colours.copy()
        # Initialize a grid for each tube
        self.grid = np.tile(0, (self.tube_count, self.tube_count, self.tube_length, 3))
        # Load synth patch
        for synth in self.synths:
            synth.load_program()
        
    def update(self, distances):
        self.current_colours = self.base_colours.copy()
        self.grid[:] = 0 # np.nan #np.zeros([self.tube_count, self.tube_count, self.tube_length, 3])
        
        #nonzeros = (tube, distance) for tube, distance in enumerate(distances) if distance > 0
        
        for tube, distance in enumerate(distances):
            controller = self.synths[tube]      
            
            if distance > 0:
                base_colour = self.colours[tube].copy()
                # Set colour for each pixel in this column and row
                self.grid[tube, tube, :] = base_colour
                self.grid[tube, :, distance-2:distance+2] = base_colour # Wider beam
                
                # Find horizontal intersections
                # Find any to left
                current_colour = base_colour.copy()
                for t, d in reversed(list(enumerate(distances[:tube-1]))):
                    if d > 0:
                        print("left hit on tube:", t)
                        current_colour += self.colours[t]
                        # Set colours of pixels to the left of the collision on this row
                        self.grid[tube, :t, distance-2:distance+2] = current_colour
                        if d >= distance:
                            # Set colours of pixels above the collision in this column
                            self.grid[tube, t, d:] = current_colour
                        else:
                            # Set colours of pixels below the collision in this column
                            self.grid[tube, t, :d] = current_colour
                # And right
                current_colour = base_colour.copy()
                for t, d in list(enumerate(distances))[tube+1:]:
                    if d > 0:
                        print("right hit on tube:", t)
                        current_colour += self.colours[t]
                        self.grid[tube, t:, distance-2:distance+2] = current_colour
                        if d >= distance:
                            # Set colours of pixels above the collision in this column
                            self.grid[tube, tube, d:] = current_colour
                        else:
                            # Set colours of pixels below the collision in this column
                            self.grid[tube, tube, :d] = current_colour
             
                # Update synths
                #
                # Set modulation and ensure sound playing
                controller.modulate(int(min(distance * self.midi_ratio, 127)))
                if not controller.playing:
                    controller.start()                
                
            else:
                
                # Stop the synth
                if controller.playing:
                    controller.stop()          
        
        self.current_colours = np.clip(np.sum(self.grid, axis = 0), 0, 255).astype(np.uint8)
        
        return self.current_colours             
        
class test_AAAALightBlender:    
    
    def __init__(self, tube_count, led_per_tube):
        self.tube_length = led_per_tube
        self.tube_count = tube_count
        self.midi_ratio = 127.0/led_per_tube
        self.midi_program = 3
        self.midi_velocity = 112
        self.midi_modulation = 1
        
        self.colours = np.array(lighttools.sinebow(80))
        print(self.colours)
        self.colour_step = 20

        notes = [i + 12 for i in [45, 47, 48, 50, 52, 53, 56, 57]]
        # synth(channel, program, note, velocity, modulation)
        self.synths = [synths.syn_Midi(n, self.midi_program, notes[n], self.midi_velocity, self.midi_modulation)
                        for n in range(self.tube_count)]
        self.tick = 0
    
    def load(self):    
       
        # Set all pixels to black
        black = np.array([0, 0, 0])               
        self.current_colours = np.tile(black, (self.tube_count, self.tube_length, 1))
        self.base_colours = self.current_colours.copy()
        # Initialize a grid for each tube
        self.grid = np.tile(0, (self.tube_count, self.tube_length, 1))
        # Load synth patch
        for synth in self.synths:
            synth.load_program()
        
    def update(self, distances):
        self.current_colours = self.base_colours.copy()
        self.grid[:] = 0 # np.nan #np.zeros([self.tube_count, self.tube_count, self.tube_length, 3])
        
        #nonzeros = (tube, distance) for tube, distance in enumerate(distances) if distance > 0
        
        for tube, distance in enumerate(distances):
            controller = self.synths[tube]      
            
            if distance > 0:
                # Set colour for each pixel in this column and row
                # All pixels in this column
                self.grid[tube, :] += self.colour_step                
                # All columns in this row apart from this one, 2 rows either side to compensate for resolution
                self.grid[:tube, distance-2:distance+2] += self.colour_step
                self.grid[tube+1:, distance-2:distance+2] += self.colour_step
                
                # Find horizontal intersections
                # Find any to left
                for t, d in reversed(list(enumerate(distances[:tube]))):
                    if d > 0:
                        print("left hit on tube:", t)
                        # Set colours of pixels to the left of the collision on this row
                        self.grid[:t, distance-2:distance+2] += self.colour_step
                        if d < distance:
                            # Set colours of pixels above the collision in this column
                            self.grid[t, distance:] += self.colour_step
                        else: 
                            # Set colours of pixels below the collision in this column
                            self.grid[t, :distance] += self.colour_step
                # And right
                for t, d in list(enumerate(distances))[tube+1:]:
                    if d > 0:
                        print("right hit on tube:", t)
                        self.grid[t+1:, distance-2:distance+2] += self.colour_step
                        if d < distance:
                            # Set colours of pixels above the collision in this column
                            self.grid[t, distance+1:] += self.colour_step
                        else:
                            # Set colours of pixels below the collision in this column
                            self.grid[t, :distance-1] += self.colour_step
                
                # Update synths
                #
                # Set modulation and ensure sound playing
                controller.modulate(int(min(distance * self.midi_ratio, 127)))
                if not controller.playing:
                    controller.start()                
                
            else:
                
                # Stop the synth
                if controller.playing:
                    controller.stop()          
         
        for position, val in np.ndenumerate(self.grid):                
            colour = self.colours[val%80] if val > 0 else np.array([0, 0, 0])
            self.current_colours[position[0]][position[1]] = colour 
        
        return self.current_colours             
        
        




    
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
