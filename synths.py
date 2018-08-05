import sc, time
from rtmidi.midiutil import open_midioutput
from rtmidi.midiconstants import NOTE_OFF, NOTE_ON, CONTROL_CHANGE, PROGRAM_CHANGE, ALL_NOTES_OFF

print("Setting up midi")
try:
    global midiout, port_name
    midiout, port_name = open_midioutput(2, 1)
except (EOFError, KeyboardInterrupt):
    sys.exit()
    # arg out = 0, pan = 0.0, freq = 440, amp = 0.1, gate = 1,
    # att = 0.01, dec = 0.5, sus = 1, rel = 0.5
    # lforate = 10, lfowidth = 0.01, cutoff = 100, rq = 0.5;
    
    min = 500 # min cutoff
    
    def __init__(self, freq):
        path = "organdonor"
        synth = sc.Synth(path, 3000 + freq)
        synth.amp = 0.7
        synth.lforate = 1
        synth.lfowidth = 0
        synth.cutoff = 6000
        synth.gate = 0
        synth.run(1)
        synth.rq = 0.1
        synth.rel = 1
        synth.freq = freq # * 2    
        self.synth = synth        
        self.playing = False
    
    def modulate(self, value): # Input range 0 - 1000
        self.synth.lforate = (value/8.)
        self.synth.lfowidth = value/10000.
        self.synth.cutoff = value * 50.
        
    def start(self):
        self.synth.run(1)
        self.synth.gate = 1
        self.playing = True
        
    def stop(self):
        self.synth.gate = 0
        #self.synth.run(0)
        self.playing = False
    
    def end(self):
        self.synth.run(0)
     
class syn_Midi():
    
    def __init__(self, channel, program, note, velocity, modulation):        
        self.channel = channel
        self.note = note
        self.modulation = modulation
        self.note_on = [NOTE_ON + channel, note, velocity]
        self.note_off = [NOTE_OFF + channel, note, 0]
        self.midi_program = program
    
    def load_program(self):
        self.playing = False
        midiout.send_message([ALL_NOTES_OFF + self.channel, 0])
        midiout.send_message([PROGRAM_CHANGE + self.channel, self.midi_program])
        time.sleep(0.05)
        midiout.send_message([ALL_NOTES_OFF + self.channel, 0])
        print([PROGRAM_CHANGE + self.channel, self.midi_program])
    
    def modulate(self, value): # Input range 0 - 127
        modulate = [CONTROL_CHANGE  + self.channel, self.modulation, value]
        print(modulate)
        midiout.send_message(modulate)
        
    def start(self):
        self.playing = True
        print(self.note_on)
        midiout.send_message(self.note_on)
        
    def stop(self):
        self.playing = False
        midiout.send_message(self.note_off)
    
    def end(self):
        pass   