# Manage an array of Benewake TFMini laser distance sensors connected by serial

#### CONSTANTS ####
#
# tfMini config commands. Enter config, send any number of config commands, then exit.
#
TFMINI_ENTER_CONFIG = "\x42\x57\x02\x00\x00\x00\x01\x02"
TFMINI_SET_UNITS_MM = "\x42\x57\x02\x00\x00\x00\x00\x1A"
TFMINI_SET_SERIAL = "\x42\x57\x02\x00\x00\x00\x01\x06"
TFMINI_EXIT_CONFIG = "\x42\x57\x02\x00\x00\x00\x00\x02"
TFMINI_AUTOMATIC_DISTANCE_MODE = "\x42\x57\x02\x00\x00\x00\x00\x14"
TFMINI_MANUAL_DISTANCE_MODE = "\x42\x57\x02\x00\x00\x00\x01\x14"
TFMINI_SHORT_DISTANCE_MODE = "\x42\x57\x02\x00\x00\x00\x02\x11"
TFMINI_LONG_DISTANCE_MODE = "\x42\x57\x02\x00\x00\x00\x07\x11"

# These commands do not require exiting config mode; they may require serial to be restarted however.
TFMINI_RESET_ALL_SETTINGS = "\x42\x57\x02\x00\xFF\xFF\xFF\xFF" 
TFMINI_SET_BAUD_RATE = "\x42\x57\x02\x00\x00\x00\xFF\x08"  # Where FF is a byte from 0x00 to 0x0c for 9600 to 51200 baud

import serial, time, curses, os

ports = []

def init(devices):
    for device in devices:
        print("Starting serial on device: %s" % device)
        port = serial.Serial(device, baudrate=115200, timeout=0.5)
        ports.append(port)  
        port.flushInput()
        
        #print("Writing init strings")
        
        #port.write(TFMINI_ENTER_CONFIG) # Enter config mode
        #time.sleep(0.1)
        #port.write(TFMINI_RESET_ALL_SETTINGS)
        #time.sleep(0.1)
        #port.write("\x42\x57\x02\x00\x00\x00\x06\x08") # Set baud rate - penultimate byte 0x06=115200, 0x00=9600
        #time.sleep(0.1)
        #port.write(TFMINI_SET_UNITS_MM) # Set to read in mm
        #time.sleep(0.2)
        #port.write(TFMINI_MANUAL_DISTANCE_MODE) #
        #time.sleep(0.2)
        #port.write(TFMINI_SHORT_DISTANCE_MODE) #
        #time.sleep(0.2)
        #port.write(TFMINI_EXIT_CONFIG) # Exit config mode
        time.sleep(0.1)
        
        print("%s initialised" % device)

    print("Sensors initialised on %d ports" % len(ports))

def get_reading(portnumber):
    
    port = ports[portnumber]
    
    # Data Format for Benewake TFmini
    #===============================
    # 9 bytes total per message:
    # 1) 0x59 ("Y")
    # 2) 0x59 ("Y")
    # 3) Dist_L (low 8bit)
    # 4) Dist_H (high 8bit)
    # 5) Strength_L (low 8bit)
    # 6) Strength_H (high 8bit)
    # 7) Reserved bytes (Shows whether the TFMini has chosen short or long sensing mode - 2 for short, 7 for long
    # 8) Original signal quality degree
    # 9) Checksum parity bit (low 8bit), Checksum = Byte1 + Byte2 +...+Byte8
    if port.inWaiting() > 8:
        try:            
            buffer = port.read(port.inWaiting())
            #print buffer
            packet_start = buffer.find("YY") + 2
            packet_length = 7
            last = buffer[packet_start:packet_start + packet_length]
            #last = buffer.split("YY")[-2:-1][0] # Grab the last-but-one packet in case the last is incomplete.            
            # Distance
            low = ord(last[0])
            high = ord(last[1])
            distance = (high << 8) + low
            # Signal Strength
            low = ord(last[2])
            high = ord(last[3])
            strength = (high << 8) + low
            # Short/long mode
            reserved = ord(last[4])
            # Quality - appears to be unused
            quality = ord(last[5])
            checksum = ord(last[6])
            return distance, strength, quality, reserved
        except Exception as e:
            print("Error parsing serial data. Bytes: {} Last: {}".format(len(buffer), last))            
            #print(buffer)
    else:
        print("Underrun. Bytes: {}".format(port.inWaiting()))
    return (0, 0, 0, 0) # Return dummy data so program can continue.

if __name__ == "__main__":

    init(devices = ["/dev/tty-U" + str(i) for i in range(8)]) # ttyUSB0 --> ttyUSB8)

    stdscr = curses.initscr()
    
    #try:
    while True:        
        for portnumber, _ in enumerate(ports):
            distance, strength, quality, reserved = get_reading(portnumber)
            #print("Laser: %d Dist: %d Strength: %d Quality: %d Reserved: %d" %(portnumber, distance, strength, quality, reserved))
            stdscr.addstr(portnumber, 0, "Laser: %d Dist: %d Strength: %d Quality: %d Reserved: %d" %(portnumber, distance, strength, quality, reserved))
            time.sleep(0.02)
            stdscr.refresh()
    #except: # Exception as e:
        # print(e.message)
        # Fix console after curses
        #curses.endwin()
        #os.system('stty sane')
        # raise e