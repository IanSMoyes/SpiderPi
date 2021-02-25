# This will be the final code to run Goofy's lights
import board, busio, neopixel, time, adafruit_dotstar

dotstar = adafruit_dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1)

print ("Waiting a minute while the Raspberry Pi gets it's head straight")
time.sleep(60)
print("OK, ready? Let's twinkle!")

UART = busio.UART(board.TX,board.RX,baudrate=115200, timeout=1.0) # Define UART port

TRINKET_FRAME_HEADER = b'\x25\x25' # Define data frame header

# Define lights
# 2 NeoPixel strips of 8 GRBW LEDs each connected on D2 with autowrite off
# These will become the head & tail lights
HEADTAILPIXELS = 16
headtailpixels = neopixel.NeoPixel(board.D2, HEADTAILPIXELS, brightness=0.4, pixel_order=neopixel.GRBW, auto_write=False)
# NeoPixel ring of 12 pixels on D0 with autowrite on
# These will become the face lights
FACEPIXELS = 12
facepixels = neopixel.NeoPixel(board.D0, FACEPIXELS, brightness=0.05, pixel_order=neopixel.GRBW, auto_write=True)

# Colours for head/tail lights
AMBER = (96,45,0,0) # Indicators
RED = (64,0,0,0) # Tail lights
WHITE = (0,0,0,255) # Head lights
GREY = (0,0,0,32) # Reversing lights
BLACK = (0,0,0,0) # Lights off!

def colourwheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        return 0, 0, 0
    if pos < 85:
        return int(255 - pos * 3), int(pos * 3), 0
    if pos < 170:
        pos -= 85
        return 0, int(255 - pos * 3), int(pos * 3)
    pos -= 170
    return int(pos * 3), 0, int(255 - (pos * 3))

def checksum(buf):
    '''Calculate the checksum
    :param buf: data frame received
    :return: checksum calculated
    '''
    sum = 0x00
    for b in buf:  # scan the buffer
        sum += b # sum the contents of the buffer
    sum = ~sum  # Negate the sum (change the sign)
    return sum & 0xff # return the 8 least significant bits

def read_data():
    recv_data = UART.readline() # Read a \n terminated line from the UART port
    if recv_data != None: # If the buffer was not empty
        UART.reset_input_buffer() # Clear the buffer
        try:
            data_ok = recv_data[-2] == checksum(recv_data[2:-2]) # Do the checksums match?
            # Does the data have a valid header
            data_ok = data_ok and recv_data[0:2] == TRINKET_FRAME_HEADER
            # Is the data the right length
            data_ok = data_ok and len(recv_data) == 8
            if data_ok:
                LED = int(recv_data[2]) # Extract the LED to be lit
                colour = ()
                for i in range(3): # Extract the direction or colour data
                    colour += (int(recv_data[i+3]), )
                return LED, colour
        except BaseException as e: # If it all went wrong
            print(e) # Print the explanation
    return None, None # If the data frame was empty, or corrupt

# Define functions to handle different directions
def left(): # This is what to do if the robot is turning left
    print("Turning left")
    global flashon
    if flashon: # Indicate left
        headtailpixels[7] = (AMBER)
        headtailpixels[15] = (AMBER) # In America you'll want the rear indicators RED
    else:
        headtailpixels[7] = (BLACK)
        headtailpixels[15] = (BLACK)
    headtailpixels[0] = (BLACK) # Turn the right indicators off
    headtailpixels[8] = (BLACK)

def right(): # this is what to do if the robot is turning right
    print("Turning right")
    global flashon
    if flashon: # Indicate right
        headtailpixels[0] = (AMBER)
        headtailpixels[8] = (AMBER) # In America you'll want the rear indicators RED
    else:
        headtailpixels[0] = (BLACK)
        headtailpixels[8] = (BLACK)
    headtailpixels[7] = (BLACK) # Turn the left indicators off
    headtailpixels[15] = (BLACK)

def straight(): # this is what to do if the robot is going straight
    print("Proceeding straight")
    headtailpixels[0] = (BLACK) # Turn off the indicators
    headtailpixels[7] = (BLACK)
    headtailpixels[8] = (BLACK)
    headtailpixels[15] = (BLACK)

def hazards(): # this is what to do if there is a hazard
    print("Hazard detected")
    global flashon
    if flashon: # Flash all the indicators
        headtailpixels[0] = (AMBER)
        headtailpixels[7] = (AMBER)
        headtailpixels[8] = (AMBER) # In America you'll want the back indicators RED
        headtailpixels[15] = (AMBER)
    else: # Turn all the indicators off
        headtailpixels[0] = (BLACK)
        headtailpixels[7] = (BLACK)
        headtailpixels[8] = (BLACK)
        headtailpixels[15] = (BLACK)

def stopped(): # this is what to do if the robot is stopped
    for i in range(HEADTAILPIXELS): headtailpixels[i] = (BLACK) # Turn off all the lights

def forward(): # This is what to do if the robot is going forwards
    print("Proceeding forward")
    headtailpixels[1] = (RED) # Turn on the tail lights
    headtailpixels[6] = (RED)
    for i in range(2,6): headtailpixels[i] = (BLACK) # Turn off the reversing lights
    for i in range(9,15): headtailpixels[i] = (WHITE) # Turn on the head lights

def back(): # This is what to do if the robot is reversing
    print("Reversing")
    global flashon
    if flashon: # Flash the reversing lights
        for i in range(1, 7): headtailpixels[i] = (GREY)
    else:
        for i in range(1,7): headtailpixels[i] = (BLACK)
    for i in range(9, 15): headtailpixels[i] = (BLACK) # Turn the headlights out

def twinkle(LED, colour):
    colour += (0, ) # Don't use a white value as it washes out the colour

    print("LED ID:", LED, "Colour:", colour)
    facepixels[LED] = colour # Update the face pixel

# Used to facilitate turning the flashing lights on & off every second
starttime = time.monotonic()
# Used to store the direction of the robot (forward, reverse, stopped)
direction = 0
# Used to store the rotational state of the robot (left, right, straight or hazard)
turning = 0
# Used to store whether the flashing lights are currently on or off
flashon = False
# Used to turn off the facepixels after a while
data_received =  time.monotonic()

dotstar.brightness = 1 # Little colour fanfare to signify we're ready
for pos in range(255): # Once round the wheel
    colour = colourwheel(pos)
    dotstar[0] = colour
    facepixels[pos % FACEPIXELS] = colour
    headtailpixels[pos % HEADTAILPIXELS] = colour
    headtailpixels.show() # autoshow is off
    time.sleep(0.001)
dotstar[0] = (0,0,0) # Turn the lights off at the end
facepixels.fill((0,0,0,0)) # autoshow is on
stopped()
headtailpixels.show() # autoshow is off

# Main loop
while True: # forever
    current = time.monotonic()
    if current >= starttime + 1: # Switch state of indicators
        starttime = current
        flashon = ~flashon
        if direction == 2: back() # Flash the appropriate lights
        if turning == 1: right()
        elif turning == 2: left()
        elif turning == 3: hazards()

    LED, colour = read_data() # Read from the UART
    if LED is None: # If there's no data turn the face lights out
        if data_received + 3 <time.monotonic():
            facepixels.fill((0,0,0,0)) # autoshow is on
    else: # If there is data, process it
        data_received = time.monotonic()
        if LED == 12: # If the data is a direction code
            # Do some magic
            direction = colour[0] # Set the direction flag
            turning = colour[1] # Set the turning flag
            if direction == 0: stopped() # Call the cooresponding direction function
            elif direction == 1: forward()
            if turning == 0: straight() # Call the correspondng turning function
        else: # If the UART data is intended for the facepixels
            twinkle(LED, colour)
    headtailpixels.show() # autoshow is off