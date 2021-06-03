
#include <Metro.h>
#include <AltSoftSerial.h>    // Arduino build environment requires this
#include <wavTrigger.h>

wavTrigger wTrig;             // Our WAV Trigger object

Metro gLedMetro(6300);         // LED blink interval timer
Metro gSeqMetro(6300);  

void setup() {
  
  Serial.begin(9600);
  pinMode(13, OUTPUT); 
  pinMode(12, OUTPUT); 
  pinMode(9, OUTPUT);  

  
  // If the Arduino is powering the WAV Trigger, we should wait for the WAV
  //  Trigger to finish reset before trying to send commands.
  delay(1000);

  // WAV Trigger startup at 57600
  wTrig.start();  
  delay(10);

  // Send a stop-all command and reset the sample-rate offset, in case we have
  //  reset while the WAV Trigger was already playing.
  wTrig.stopAllTracks();   
  wTrig.samplerateOffset(0); 
  wTrig.masterGain(0); // volume
  
}


void loop() {

  int input = Serial.read();

  if (input == 49){

    wTrig.trackPlaySolo(2);
  }

    int sound = analogRead(A0);

    if (sound > 11){

      digitalWrite(13,HIGH); // to cyton
      digitalWrite(12,HIGH); // check osilloscope
      delay(100);
      digitalWrite(12,LOW);
      digitalWrite(13,LOW);
      
    }
  




}
