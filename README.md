# Auditory BCI for real-time AAD

This is Auditory BCI for Oddball Task.

It can not only collect EEG data from human brain, but it can play sounds and record triggers corresponding to sound.


## Requirements

1. OpenBCI (for EEG data acquisition)

    : OpenBCI cyton + daisy

    : EEG Electrode Cap

    https://openbci.com/

2. Arduino UNO (for Trigger)

    https://www.arduino.cc/

3. WAV Trigger (for sound play)

    : SD card

    https://www.sparkfun.com/products/13660

---------------------------

## OpenBCI 

For OpenBCI board running with Arduino IDE, see the OpenBCI Tutorial and Library.

https://docs.openbci.com/docs/02Cyton/CytonProgram

https://github.com/OpenBCI/OpenBCI_Cyton_Library

------------------------------

## Python LSL

- Lab Streaming Layer (LSL) with python

https://docs.openbci.com/docs/06Software/02-CompatibleThirdPartySoftware/LSL

+ We use advanced LSL code ( Not OpenBCI_LSL library )

https://docs.openbci.com/docs/09Deprecated/Python

-------------------------------

## WAV Trigger

WAV Trigger Tutorial & Library

http://robertsonics.com/2015/04/25/arduino-serial-control-tutorial/

https://github.com/robertsonics/WAV-Trigger-Arduino-Serial-Library

---------------------------------

## Sound

length : 100ms
r/f : 5ms
Standard : 1000Hz
Target : 2000Hz

------------------------------
## Device Paradigm

1. Start streaming using python (LSL) > EEG acquisition start.
2. Start Experiment using psychopy.
3. Send signal for sound onset to Arduino through Serial Port.
4. play sound from WAV Trigger through arduino ( generate jitter ) and send Triggers for standard or target. [ 1. line ]
5. Flow Sound through earphon to subject and analog signal of sound to arduino. [ 2. line ]
6. Detect sound onset timing in arduino by analog signal of sound. [ 3. line ]
7. Send tigger about sound onset to Cyton + daisy ( No jitter ). [ 4. line ]
8. Send EEG data and Trigger to desktop, be received and recorded by python.



![Device paradigm_oddball (1)](https://user-images.githubusercontent.com/85104167/120580345-fd92e100-c463-11eb-9166-1731674b8ad1.jpg)

