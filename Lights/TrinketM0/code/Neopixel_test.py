# Neopixel test code
import board, busio, neopixel, time
from random import random

# Define lights
# 2 NeoPixel strips of 8 GRBW LEDs each connected on D2 with autowrite off
# These will become the head & tail lights
HEADTAILPIXELS = 16
headtailpixels = neopixel.NeoPixel(board.D2, HEADTAILPIXELS, brightness=0.6, pixel_order=neopixel.GRBW, auto_write=False)
# NeoPixel ring of 12 pixels on D0 with autowrite on
# These will become the face lights
FACEPIXELS = 12
facepixels = neopixel.NeoPixel(board.D0, FACEPIXELS, brightness=0.02, pixel_order=neopixel.GRBW, auto_write=True)

# Main loop
while True:
    for i in range(FACEPIXELS-1):
        facepixels[i] = facepixels[i+1]
    facepixels[FACEPIXELS-1] = (int(random()*255.9), int(random()*255.9), int(random()*255.9), 0)
    for i in range(HEADTAILPIXELS-1):
        headtailpixels[i] = headtailpixels[i+1]
    headtailpixels[HEADTAILPIXELS-1] = (int(random()*255.9), int(random()*255.9), int(random()*255.9), 0)
    headtailpixels.show() # autoshow is off
    time.sleep(0.1)