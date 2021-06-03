// Oddball

#include <Metro.h>
#include <AltSoftSerial.h>    // Arduino build environment requires this
#include <wavTrigger.h>

wavTrigger wTrig;             // Our WAV Trigger object

Metro gLedMetro();         // LED blink interval timer
Metro gSeqMetro();        // Sequencer state machine interval timer


void setup() {

  Serial.begin(9600);
  randomSeed(analogRead(0));

  pinMode(9, OUTPUT);  // WAV Trigger Write signal
  pinMode(13, OUTPUT); // Cyton Write signal
  pinMode(12, OUTPUT);  

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

int b = 11;
int a = 1;
int s;
int i;

int trial = 365;  // total trial - 10
int ran[365];
int arr[365];
int cnt = 1;
int temp;
int ch;
int c = 1;
int block = 1;
int target;


///////////////////
void loop() {
  
digitalWrite(3, HIGH);


///// Change ratio of target sound per block 
if (block == 1){
  target = round((trial+10)*0.25);
  
}
else if (block == 2){
  target = round((trial+10)*0.15);
  
}
else if (block == 3){
  target = round((trial+10)*0.20);
}

//Serial.println(target);
//Serial.println(block);

//////////// Random Seed ////////////////

// To avoid repetition
if (cnt == 1){

  // Seed first random int
  ran[0] = random(1, trial+1);


  // Run as the number of trial corresponding to the current block
  for (i = 1; i < trial; ){  
    
    temp = random(1,trial+1);

     
     for (cnt = 0; cnt < i; cnt++){

      // if current random int is duplicated, return to pre-steop
      if (ran[cnt] == temp ){            
        break;
      }
      
      // 
      else if (ran[cnt] != temp && cnt == i-1){
         
        ran[i] = temp;
        
        if ( temp > target){
          arr[i] = 0;
        }
        else{
          arr[i] = 1;
        }

        if (i < trial-10){

          if (arr[cnt] == 1 && arr[i] == 1){
            break;
        }
        }
            
        i++;
      }  
    }  
  }
  cnt = 0;
}


/////////////////////////////////////

int input = Serial.read();
int sound = 0;

 ////// Main experiment start //////
if (input == 49){
cnt = 1;    
block = block+1;     

    /// play Standard 10 times
    for (int s = 0; s < 10;){

    
      //// Sound onset (from arduino) ////
      
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
    
        // Random int
       a = arr[n]; 
       cnt = 1;

         // Standard sound
          if (a == 0) { 
 
            while(true) {          // To wait Analog sound detection

              if (cnt == 1){       // To avoid sound repeat
                
              //// WAV Trigger onset ////
                wTrig.trackPlaySolo(2);
            
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
                digitalWrite(13, LOW);

                delay(700);
                break;

                }    
            }
            wTrig.stopAllTracks(); 
            
          }
          // Target
          else if (a == 1){  

            int sound = analogRead(A0);
            while (true){

            // To 
              if (cnt == 1){
                
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
                digitalWrite(13, LOW);

                delay(700);
                break;
                }    
      
              wTrig.stopAllTracks(); 
                }
          }
          
        }                    
  }
  
////// Paractice sound //////

  //// Standard sound
else if (input == 50){  

    //for (s = 0; s < 3; s++){
      
      wTrig.trackPlaySolo(2);
      digitalWrite(13, HIGH);
      //delay(100);
      digitalWrite(13, LOW);        
     // }
    }

    
//// Target sound 
else if (input == 51){

  //for (s = 0; s <3; s++){

    wTrig.trackPlaySolo(3);
    digitalWrite(13, HIGH);
    //delay(800);
    digitalWrite(13, LOW);  
    //}
  }

  
//// Practice 
else if (input == 52){  

  for(s = 0; s < 10; s++){

     if (s == 4 || s == 7){
      
        wTrig.trackPlaySolo(3);
        digitalWrite(12, HIGH);
        digitalWrite(12, LOW);
        delay(800);
        wTrig.stopAllTracks();
     }
     else{

        wTrig.trackPlaySolo(2);
        digitalWrite(13, HIGH);
        digitalWrite(12, LOW);
        delay(800);  
        wTrig.stopAllTracks();   
      }
  
    } 
}

}
