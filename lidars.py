# Manage an array of Benewake TFMini laser distance sensors connected by serial

#### CONSTANTS ####
#
# tfMini config commands. Enter config, send any number of config commands, then exit.
#
TFMINI_ENTER_CONFIG = "\x42\x57\x02\x00\x00\x00\x01\x02"
TFMINI_SET_MM = "\x42\x57\x02\x00\x00\x00\x00\x1A"
TFMINI_SET_SERIAL = "\x42\x57\x02\x00\x00\x00\x01\x06"
TFMINI_EXIT_CONFIG = "\x42\x57\x02\x00\x00\x00\x00\x02"

import serial, time
num = 8
devstrings = ["/dev/ttyUSB" + str(i) for i in range(num)] # ttyUSB0 --> ttyUSBn
ports = []
distances = [0 for _ in range(8)]

def init(devices = devstrings):
    for device in devices:
        print("Starting serial on device: %s" % device)
        port = serial.Serial(device, baudrate=115200, timeout=0.5)
        ports.append(port)  
        port.flushInput()
        print("Writing init string")
        """
        port.write("\x42\x57\x02\x00\x00\x00\x01\x02") # Enter config mode
        time.sleep(0.1)
        #port.write("\x42\x57\x02\x00\xFF\xFF\xFF\xFF") # Set baud rate
        #time.sleep(0.1)
        port.write("\x42\x57\x02\x00\x00\x00\x00\x1A") # Set to read in mm
        time.sleep(0.1)
        port.write("\x42\x57\x02\x00\x00\x00\x01\x06") # Serial mode (instead of pix, which sends text not bytes)
        time.sleep(0.1)
        port.write("\x42\x57\x02\x00\x00\x00\x00\x02") # Exit config mode
        """
        #Changes to the mm:  send 42 57 02 00 00 0 01, 02 to enter configuration mode, then send 42 57 02 00 00 00 00 1A;
        #Change to cm: send 42 57 02 00 00 0 01, 02 to enter configuration mode, then send 42 57 02 00 00 00 01 1A. 
        print("%s initialised" % device) # Could check that we're receiving the expected data here...

    print("Monitoring distances on %d ports" % len(ports))

def get_reading(portnumber):
    tries = 0
    port = ports[portnumber]
    last = curr = 0
    port.flushInput()    
    while tries < 9: # Search one byte at a time for the start pattern
        try:
            curr = ord(port.read(1))
            if last == curr == 89: # We got a distance frame
                data = port.read(7)
                #print([ord(d) for d in data])
                low = ord(data[0])
                high = ord(data[1])
                distance = (high << 8) + low
                low = ord(data[2])
                high = ord(data[3])
                strength = (high << 8) + low
                reserved = ord(data[4])
                quality = ord(data[5])
                #checksum = ord(data[6])
                #distance = (distance if (portnumber == 1) or (portnumber == 5)  else distance * 10)
                return distance, strength, quality, reserved
            else: # Probably somewhere other than the start of a block.
                last = curr
                tries += 1
        except: #Something non-numerical data in the stream, probably an error
            print(port.read(300)) # Dump the error text
    
    #Either got an error or couldn't find start of data block
    return (0, 0, 0, 0) # Return dummy data so program can continue.
            

def get_distance(portnumber):
    return get_reading(portnumber)[0]

if __name__ == "__main__":
    init()
        
    while True:
        # Data Format for Benewake TFmini
        #===============================
        # 9 bytes total per message:
        # 1) 0x59
        # 2) 0x59
        # 3) Dist_L (low 8bit)
        # 4) Dist_H (high 8bit)
        # 5) Strength_L (low 8bit)
        # 6) Strength_H (high 8bit)
        # 7) Reserved bytes
        # 8) Original signal quality degree
        # 9) Checksum parity bit (low 8bit), Checksum = Byte1 + Byte2 +...+Byte8
            
        for portnumber, _ in enumerate(ports):
            distance, strength, quality, reserved = get_reading(portnumber)
            print("Laser: %d Dist: %d Strength: %d Quality: %d Reserved: %d" %(portnumber, distance, strength, quality, reserved))
            time.sleep(0.02)
            
            '''
            data = port.read(9)
            #print(rcv)
            test, test2 = ord(rcv[0]), ord(rcv[1]) # expect 89, 89        
            low = ord(rcv[2])
            high = ord(rcv[3])
            quality = ord(rcv[8])
            distance = (high << 8) + low
            print("%d - %d - %d - %d" % (distance, low, high, qual))
            time.sleep(0.01)
            '''