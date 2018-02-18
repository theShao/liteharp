import sc, time

class syn_Moog():    
    # moogbass synthdef from Steal this Sound
    # arg out = 0, pan = 0, freq = 440, amp = 0.1, gate = 1, cutoff = 1000, gain = 2.0,
    # lagamount = 0.01, att = 0.001, dec = 0.3, sus = 0.9, rel = 0.2, chorus = 0.7;
    
    min = 1000 # min cutoff
    
    def __init__(self, freq):
        path = "moogbass"
        synth = sc.Synth(path, 2000 + freq)
        time.sleep(0.1)
        synth.cutoff = self.min # LPFilter freq
        synth.gain = 3 # Filter gain
        synth.amp = 0.5#
        synth.rel = 2 #
        #synth.att = 2
        synth.chorus = 0
        synth.gate = 0        
        synth.freq = freq    
        self.synth = synth        
        self.playing = False
    
    def modulate(self, value): # Input range 0 - 1000
        self.synth.cutoff = value * 2 + self.min
        self.synth.chorus = value/250.
        
    def start(self):
        self.synth.run()
        self.synth.gate = 1
        self.playing = True
        
    def stop(self):
        self.synth.gate = 0
        self.playing = False

class syn_Lead():    
    
    min = 200 # min cutoff
    
    def __init__(self, freq):
        path = "cs80lead_mh"
        synth = sc.Synth(path, 6000 + freq, args=["freq", freq])
        time.sleep(0.1)
        synth.cutoff = self.min # LPFilter freq
        synth.gate = 0
        synth.sus = 2
        synth.fsus = 2
        synth.vibrate = 10
        synth.freq = freq    
        self.synth = synth        
        self.playing = False
    
    def modulate(self, value): # Input range 0 - 1000
        self.synth.cutoff = int(value / 5) + self.min
        self.synth.vibrate = value/100
        
    def start(self):
        self.synth.run()
        self.synth.gate = 1
        self.playing = True
        
    def stop(self):
        self.synth.gate = 0
        self.playing = False

        

class syn_AM():    
    # moogbass synthdef from Steal this Sound
    # arg out = 0, pan = 0, freq = 440, amp = 0.1, gate = 1, cutoff = 1000, gain = 2.0,
    # lagamount = 0.01, att = 0.001, dec = 0.3, sus = 0.9, rel = 0.2, chorus = 0.7;
    
    min = 1000 # min cutoff
    
    def __init__(self, freq):
        path = "AM"
        synth = sc.Synth(path, 4000 + freq)
        time.sleep(0.1)
        synth.modfreq = 1
        synth.amp = 0.5#
        synth.rel = 2 #
        #synth.att = 2
        #synth.chorus = 0
        synth.gate = 0        
        synth.freq = freq
        self.synth = synth        
        self.playing = False
    
    def modulate(self, value): # Input range 0 - 1000
        self.synth.modfreq = value * 2        
        
    def start(self):
        self.synth.run()
        self.synth.gate = 1
        self.playing = True
        
    def stop(self):
        self.synth.gate = 0
        self.playing = False
        
class syn_Saw():    
    # arg freq=440, amp=0.3, fat=0.0033, ffreq=2000, atk=0.001, dec=0.3, sus=0.5, rls=0.1,gate=1;
    
    min = 500 # min cutoff
    
    def __init__(self, freq):
        path = "fatsaw"
        synth = sc.Synth(path, 1000 + freq)    
        synth.ffreq = self.min # LPFilter freq
        synth.fat = 0.5 # Filter gain
        synth.sus = 0.9
        synth.rls = 2
        synth.amp = 0.3        
        synth.gate = 0        
        synth.freq = freq    
        self.synth = synth        
        self.playing = False
    
    def modulate(self, value): # Input range 0 - 1000
        self.synth.ffreq = value * 2 + self.min
        self.synth.fat = value/1000.
        
    def start(self):
        self.synth.gate = 1
        self.playing = True
        
    def stop(self):
        self.synth.gate = 0
        self.playing = False
       
class syn_Organdonor():    
    # arg out = 0, pan = 0.0, freq = 440, amp = 0.1, gate = 1,
    # att = 0.01, dec = 0.5, sus = 1, rel = 0.5
    # lforate = 10, lfowidth = 0.01, cutoff = 100, rq = 0.5;
    
    min = 500 # min cutoff
    
    def __init__(self, freq):
        path = "organdonor"
        synth = sc.Synth(path, 3000 + freq)
        synth.sus = 0.9
        synth.rls = 2
        synth.amp = 0.3
        synth.lforate = 10
        synth.lfowidth = 0.01
        synth.gate = 0        
        synth.freq = freq # * 2    
        self.synth = synth        
        self.playing = False
    
    def modulate(self, value): # Input range 0 - 1000
        self.synth.lforate = value/10
        self.synth.lfowidth = value/1000000
        
    def start(self):
        self.synth.gate = 1
        self.playing = True
        
    def stop(self):
        self.synth.gate = 0
        self.playing = False