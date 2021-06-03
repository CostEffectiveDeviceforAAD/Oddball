// Oddball

#include <Metro.h>
#include <AltSoftSerial.h>    // Arduino build environment requires this
#include <wavTrigger.h>

wavTrigger wTrig;             // Our WAV Trigger object

Metro gLedMetro(500);         // LED blink interval timer
Metro gSeqMetro(6000);        // Sequencer state machine interval timer


void setup() {

  Serial.begin(9600);

  pinMode(9, OUTPUT);   // Write signal to WAV Trigger
  pinMode(11, OUTPUT);  // Trigger for Standard sound
  pinMode(12, OUTPUT);  // Trigger for real sound on set  
  pinMode(13, OUTPUT);  // Trigger for Target sound
  

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

  // Sound volume control
  wTrig.masterGain(0);
  
}

int a;
int r;
int cnt = 1;
int c = 1;
int block = 1;
int target;

void loop() {
  
int trial = 375;
int ran[trial];

// To reset random int 
randomSeed(analogRead(1));

///// Change ratio of target sound per block 
if (block == 1){
  target = round((trial)*0.25);
  
}
else if (block == 2){
  target = round((trial)*0.15);
  
}
else if (block == 3){
  target = round((trial)*0.20);
}


//////////// Random Seed ////////////////

// To avoid Repetition
if (cnt == 1){

  // Make zeros array
  for (int i = 0; i < trial; i++){
    
      ran[i] = 0;
  }

  // Seed number 1(meaning target) per the number of target 
  for (int i = 0; i < target;){
    
    r = random(11,trial+1);   // 1~10 must be 0 (meaning standard)

    // To avoid continuous playback of target sounds.
    if (ran[r-2] != 1 && ran[r-1] != 1 && ran[r] != 1 && ran[r+1] != 1){
  
      ran[r] = 1;
      i++;     
    } 
  
  cnt = 0;
}
}

////////////////////////////////////////////////////////
////////////////// START STREAMING /////////////////////
////////////////////////////////////////////////////////

int input = Serial.read();
int sound = 0;

 ////// Main experiment start //////
if (input == 49){
  
  cnt = 1;    
  block = block+1;     

    /// play Standard 10 times
    for (int s = 0; s < 10;){

      //// Sound onset (from arduino) ////
      
      // To play a sound only one   
      if (cnt == 1){
        
        // WAV Trigger onset
        wTrig.trackPlaySolo(2);
    
        // WAT Trigger signal
        digitalWrite(13, HIGH);   
        cnt = 0; 
      }
          
      //// Sound read ////
      int sound = analogRead(A0);
      
      //// Sound onset detect ////
      if (sound > 12){

        // Send Trigger to Cyton during 100ms
        digitalWrite(12, HIGH);
        delay(100);
        digitalWrite(12, LOW);
        digitalWrite(13, LOW);
        
        s++;
        cnt = 1;
        
        delay(700);
      }    

      wTrig.stopAllTracks(); 
          
    }

    // Start Random play
    for (int n = 0; n < trial; n++) {      
    
       // Detect whether standard or target
       a = ran[n]; 
       cnt = 1;

       //===== Standard sound =====//
          if (a == 0) { 
 
            while(true) {          // To wait Analog sound detection

              if (cnt == 1){       // To avoid sound repeat
                
              //// WAV Trigger onset ////
                wTrig.trackPlaySolo(2);
            
              // WAT Trigger onset signal_1
                digitalWrite(11, HIGH);   
                cnt = 0; 
              }
              
              //// Sound read ////
              int sound = analogRead(A0);
              
              //// Sound onset detect ////
              if (sound > 11){
                
                digitalWrite(12, HIGH);
                delay(100);

               // Trigger offset
                digitalWrite(12, LOW);
                digitalWrite(13, LOW);

                delay(700);
                
                break;    // Towards the next array number

                }    
            }
            
           wTrig.stopAllTracks(); 
            
          }
          
        //===== Target sound =====//
          else if (a == 1){  

            while (true){       // To wait Analog sound detection

              if (cnt == 1){    // To avoid sound repeat
                
            // WAV Trigger onset
              wTrig.trackPlaySolo(3);
          
            // WAT Trigger onset signal_1
              digitalWrite(13, HIGH);   
              cnt = 0; 
              }
                
              //// Sound read ////
              int sound = analogRead(A0);
              
              //// Sound onset detect ////
              if (sound > 11){
            
                digitalWrite(12, HIGH);
                delay(100);
                
               // Trigger offset
                digitalWrite(12, LOW);
                digitalWrite(11, LOW);

                delay(700);
                
                break;    // Towards the next array number
                }    
      
              wTrig.stopAllTracks(); 
            }
          }
          
       } // End a block                   
  }

  
////// Paractice sound //////

//===== Standard sound =====//
else if (input == 50){  
      
      wTrig.trackPlaySolo(2);
      
    }
    
//===== Target sound =====//
else if (input == 51){

    wTrig.trackPlaySolo(3);

  }

//===== Practice =====//
else if (input == 52){  

  for(int s = 0; s < 10; s++){

     if (s == 4 || s == 7){
      
        wTrig.trackPlaySolo(3);
        delay(800);
        wTrig.stopAllTracks();
     }
     else{

        wTrig.trackPlaySolo(2);
        delay(800);  
        wTrig.stopAllTracks();   
      }
  
    } 
}

}
