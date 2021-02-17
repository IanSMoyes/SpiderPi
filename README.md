# SpiderPi
This repository will hold the code I'm writing to autonomously run my HiWonder SpiderPi hexapod.

## Let's be clear. My code is for MY robot. You are welcome to use it but, the only warrantee it comes with is, it's useless. I offer NO SUPPORT. Other than, if it doesn't work for you, delete it. On the other hand, if you have ANY suggestions for impovements, or you want to share your experiences, PLEASE pipe up. :-)

My ambition is to have the robot respond to voice commands with vocal responses and, utilising senros fusion, SLAM & IK, travel between pre-defined destinations inside our home aviding obstacles. Then use it to take over the World.

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
Although the robot has stock Python code to make it "do tricks", I'm developing that & writing my own code for the control layers.

2: I upgraded the Raspberry Pi for an 8Gb version, with a 256Gb SD card. I added a fan HAT. I am in the process of adding an Adafruit Trinket M0 as a BRGW Neopixel controller for front & rear "car" lights (2 strips of 8 LEDS) & audio responsive "face" accent lights (a ring of 12 LEDs). I'm also in the processs of upgrading the MPU to a 9250/BMP280 to add magnetometric measurements, ambient temperature & baromentric pressure (I might use these to increase the accuracy of the HC-SR04). I also have a 8000mAh battery to show horn in (somehow). I have ROS, OpenCV & Pytorch installed & am planning to learn how to utilise them, one day.
