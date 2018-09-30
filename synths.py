import time
from rtmidi.midiutil import open_midioutput
from rtmidi.midiconstants import NOTE_OFF, NOTE_ON, CONTROL_CHANGE, PROGRAM_CHANGE, ALL_NOTES_OFF

print("Setting up midi")
try:
    global midiout, port_name
    midiout, port_name = open_midioutput(2, 1)
except (EOFError, KeyboardInterrupt):
    sys.exit()

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