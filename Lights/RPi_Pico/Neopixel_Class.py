# Example using PIO to drive a set of WS2812 LEDs.

import array, time
import machine
import rp2

class neopixel:
    def __init__(self, channel, pixels, pin, colours=4, ):
        print("This is the constructor method.")

    self.channel = channel
    self.pixels = pixels
    self.pin = pin
    self.pull_thresh = colours * 8

    @rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=self.pull_thresh)
    def ws2812():
        T1 = 2
        T2 = 5
        T3 = 3
        wrap_target()
        label("bitloop")
        out(x, 1)               .side(0)    [T3 - 1]
        jmp(not_x, "do_zero")   .side(1)    [T1 - 1]
        jmp("bitloop")          .side(1)    [T2 - 1]
        label("do_zero")
        nop()                   .side(0)    [T2 - 1]
        wrap()

    # Create the StateMachine with the ws2812 program, outputting on Pin(22).
    self.sm = rp2.StateMachine(self.channel, self.ws2812, freq=8_000_000, sideset_base=machine.Pin(self.pin))

    # Start the StateMachine, it will wait for data on its FIFO.
    self.sm.active(1)

    # Display a pattern on the LEDs via an array of LED RGB values.
    self.ar = array.array("I", [0 for _ in range(self.pixels)])

    setpixel(self, index, colour):
        self.ar[index][0] = colour[1]
        self.ar[index][1] = colour[0]
        self.ar[index][2] = colour[2]
        if self.colours = 4:
            self.ar[index][3] = colour[3]
        self.sm.put(self.ar, 8)

    fillpixels(self, colour):
        for index in range(self.pixels):
            self.setpixel(index, colour)
'''
# Cycle colours.
for i in range(4 * self.pixels):
    for j in range(self.pixels):
        r = j * 100 // (self.pixels - 1)
        b = 100 - j * 100 // (self.pixels - 1)
        if j != i % self.pixels:
            r >>= 3
            b >>= 3
        ar[j] = r << 16 | b
    sm.put(ar, 8)
    time.sleep_ms(50)

# Fade out.
for i in range(24):
    for j in range(self.pixels):
        ar[j] >>= 1
    sm.put(ar, 8)
    time.sleep_ms(50)
'''