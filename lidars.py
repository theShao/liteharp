# Manage an array of Benewake TFMini laser distance sensors connected by serial

#### CONSTANTS ####
#
# tfMini config commands. Enter config, send any number of config commands, then exit.
#
TFMINI_ENTER_CONFIG = "\x42\x57\x02\x00\x00\x00\x01\x02"
TFMINI_SET_MM = "\x42\x57\x02\x00\x00\x00\x00\x1A"
TFMINI_SET_SERIAL = "\x42\x57\x02\x00\x00\x00\x01\x06"
TFMINI_EXIT_CONFIG = "\x42\x57\x02\x00\x00\x00\x00\x02"
TFMINI_AUTOMATIC_DISTANCE_MODE = "\x42\x57\x02\x00\x00\x00\x00\x14"
TFMINI_MANUAL_DISTANCE_MODE = "\x42\x57\x02\x00\x00\x00\x01\x14"
TFMINI_SHORT_DISTANCE_MODE = "\x42\x57\x02\x00\x00\x00\x02\x11"
TFMINI_LONG_DISTANCE_MODE = "\x42\x57\x02\x00\x00\x00\x07\x11"

# These commands do not require exiting config mode; they may require serial to be restarted however.
TFMINI_RESET_ALL_SETTINGS = "\x42\x57\x02\x00\xFF\xFF\xFF\xFF" 
TFMINI_SET_BAUD_RATE = "\x42\x57\x02\x00\x00\x00\xFF\x08"  # Where FF is a byte from 0x00 to 0x0c for 9600 to 51200 baud

import serial, time, curses

ports = []

def init(devices):
    for device in devices:
        print("Starting serial on device: %s" % device)
        port = serial.Serial(device, baudrate=115200, timeout=0.5)
        ports.append(port)  
        port.flushInput()
        
        print("Writing init strings")
        port.write(TFMINI_ENTER_CONFIG) # Enter config mode
        time.sleep(0.1)
        #port.write("\x42\x57\x02\x00\xFF\xFF\xFF\xFF") # Set baud rate
        #time.sleep(0.1)
        port.write(TFMINI_MANUAL_DISTANCE_MODE) # Set to read in mm
        time.sleep(0.1)
        port.write(TFMINI_SHORT_DISTANCE_MODE) # Serial mode (instead of pix, which sends text not bytes)
        time.sleep(0.1)
        port.write(TFMINI_EXIT_CONFIG) # Exit config mode
        
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
    if port.inWaiting() > 18:
        try:            
            buffer = port.read(port.inWaiting())
            last = buffer.split("YY")[-2:-1][0] # Grab the last-but-one packet in case the last is incomplete.
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
        except Exception as e: #Something non-numerical data in the stream, probably an error
            pass
            #print(e.message)
            #print(buffer)
    #Either got an error or couldn't find start of data block
    return (0, 0, 0, 0) # Return dummy data so program can continue.

if __name__ == "__main__":

    init(devices = ["/dev/ttyUSB" + str(i) for i in range(8)]) # ttyUSB0 --> ttyUSB8)

    stdscr = curses.initscr()
    
    try:
        while True:        
            for portnumber, _ in enumerate(ports):
                distance, strength, quality, reserved = get_reading(portnumber)
                stdscr.addstr(portnumber, 0, "Laser: %d Dist: %d Strength: %d Quality: %d Reserved: %d" %(portnumber, distance, strength, quality, reserved))
                time.sleep(0.02)
                stdscr.refresh()
    except Exception as e:
        # Fix console after curses
        os.system('stty sane')
        raise e