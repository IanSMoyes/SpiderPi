# SpiderPi
# This repository will hold the code I'm writing to autonomously run my HiWonder SpiderPi hexapod.

## Let's be clear. My code is for MY robot. You are welcome to use it but, the only warrantee it comes with is, it's useless. I offer NO SUPPORT. Other than, if it doesn't work for you, delete it. On the other hand, if you have ANY suggestions for impovements, or you want to share your experiences, PLEASE pipe up. :-)

My ambition is to have the robot respond to voice commands with vocal responses and, utilising sensor fusion, SLAM & IK, travel between pre-defined destinations inside our home, aviding obstacles.

Then use it to take over the World.

1: Out of the box robot is fitted with:
A 2Gb Raspberry Pi4.
A sophisticated servo controller which includes a 2 channel motor controller, UART, I2C, a 4 pin socket attached to 5V, GND, GPIO09 & GPIO10 (can't figure out what that one is for. Suggestions?), 8 channel 11V PWM servo controller, 6 channel 11V serial servo controller, 2 channel 5V/GND output, 2 channel 3.3V/GND ouput, 2 programmable LEDs, 2 programmeable buttons.
18 LX-224HV serial bus servos, for the legs.
2 11V PWM 9g servos, for the P&T head.
A USB video camera.
An HC-SR04.
An MPU-6050.
A robust aluminium & carbon fibre chassic.
A 2500mAh Lithium battery.
A battery voltage LCD display.
Although the robot has stock Python code to make it "do tricks", I'm developing that & writing my own code for the autonomus control layers.

2: I upgraded the Raspberry Pi for an 8Gb version, with a 256Gb SD card. I added a fan HAT. Well, I cooked the Adafruit Trinket M0 BUT, I bought a Raspberry Pi Pico and so, I am in the process of adding it as a GRBW Neopixel controller for front & rear "car" lights (2 strips of 8 LEDS) & audio responsive "face" accent lights (a ring of 12 LEDs). State Machines are strange creatures! I've also upgraded the MPU to a 9250/BMP280 to add magnetometric measurements, ambient temperature, altitude & baromentric pressure. I'm using this to increase the accuracy of the HC-SR04. I've got it working but need to reorientate the axes. I also have a 8000mAh battery to shoe horn in (somehow). I have an RPLidar A1 to install & plan to add touch sensitive toes, at one stage. I also have an Adafruit Feather M0 Express on it's way. I don't know what I'm going to use that for. I have ROS, OpenCV & Pytorch installed & am planning to learn how to utilise them, one day. One fine day I'll learn to code in C++.
