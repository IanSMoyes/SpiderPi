"""
MIT License

Copyright (c) 2021 benevpi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""

# Further development by ians.moyes@gmail.com

import array
import time
import board
# from machine import Pin
import rp2

@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
def ws2812_3():
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

@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=32)
def ws2812_4():
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

#delay here is the reset time. You need a pause to reset the LED strip back to the initial LED
#however, if you have quite a bit of processing to do before the next time you update the strip
#you could put in delay=0 (or a lower delay)
class ws2812b:
    def __init__(self, num_leds, state_machine, pin, colour_order="RGB", delay=0.001, brightness = 1, autoshow = True):
        self.num_leds = num_leds
        self.pixels = array.array("I", [0 for _ in range(num_leds)])
        self.red_shift = colour_order.index("R") * 8
        self.green_shift = colour_order.index("G") * 8
        self.blue_shift = colour_order.index("B") * 8
        self.white_shift = colour_order.find("W") * 8 # Use the "find" method in case the Neopixels are 3 colour
        if self.white_shift >= 0:
            self.sm = rp2.StateMachine(state_machine, ws2812_4, freq=8000000, sideset_base=board.pin)
        else:
            self.sm = rp2.StateMachine(state_machine, ws2812_3, freq=8000000, sideset_base=board.pin)
        """
        if self.white_shift >= 0:
            self.sm = rp2.StateMachine(state_machine, ws2812_4, freq=8000000, sideset_base=Pin(pin))
        else:
            self.sm = rp2.StateMachine(state_machine, ws2812_3, freq=8000000, sideset_base=Pin.pin))
        """
        self.sm.active(1)
        self.delay = delay
        self.brightness = brightness
        self.autoshow = autoshow

    # Set the overall value to adjust brightness when updating leds
    def set_brightness(self, brightness = None):
        if brightness == None:
            return self.brightness
        else:
            if (brightness < 0):
                brightness = 0
        if (brightness > 1):
            brightness = 1
        self.brightness = brightness
                if self.autoshow:
            self.show()

    # Create a gradient with two RGB(W) colors between "pixel1" and "pixel2" (inclusive)
    def set_pixel_line_gradient(self, pixel1, pixel2, colour1, colour2):

        right_pixel = max(pixel1, pixel2)
        left_pixel = min(pixel1, pixel2)

        for i in range(right_pixel - left_pixel + 1):
            fraction = i / (right_pixel - left_pixel)
            colour[0] = round((colour2[0] - colour1[0]) * fraction + colour1[0])
            colour[1] = round((colour2[1] - colour1[1]) * fraction + colour1[1])
            colour[2] = round((colour2[2] - colour1[2]) * fraction + colour1[2])
            if self.white_shift >= 0:
            colour[3] = round((colour2[3] - colour1[3]) * fraction + colour1[3])

            self.set_pixel(left_pixel + i, colour)
    
    # Set an array of pixels starting from "pixel1" to "pixel2" to the desired color
    def set_pixel_line(self, pixel1, pixel2, colour):
        for i in range(pixel1, pixel2+1):
            self.set_pixel(i, colour)

    # Set an individual pixel
    def set_pixel(self, pixel_num, colour):
        # Adjust color values with brightnesslevel
        red = round(colour[0] * self.brightness)
        green = round(colour[1] * self.brightness)
        blue = int(colour[2] * self.brightness)
        if self.white_shift >= 0:
            white = int(colour[3] * self.brightness)
            self.pixels[pixel_num] = white << self.white_shift | blue << self.blue_shift | green << self.green_shift | red << self.red_shift
        else:
            self.pixels[pixel_num] = blue << self.blue_shift | green << self.green_shift | red << self.red_shift
        if autoshow:
            self.show()

    # rotate x pixels to the left
    def rotate_left(self, num_of_pixels):
        if num_of_pixels == None:
            num_of_pixels = 1
        self.pixels = self.pixels[num_of_pixels:] + self.pixels[:num_of_pixels]
        if self.autoshow:
            self.show()

    # rotate x pixels to the right
    def rotate_right(self, num_of_pixels):
        if num_of_pixels == None:
            num_of_pixels = 1
        self.rotate_left(self, num_of_pixels * -1)
        if self.autoshow:
            self.show()

    def fill(self, colour):
        for i in range(self.num_leds):
            self.set_pixel(i, colour)
        time.sleep(self.delay)

    def show(self):
        for i in range(self.num_leds):
            if self.white_shift >= 0:
                self.sm.put(self.pixels[i])
            else:
                self.sm.put(self.pixels[i],8)
        time.sleep(self.delay)
