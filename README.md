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

------------------------------
## Device Paradigm

