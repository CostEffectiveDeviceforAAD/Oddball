#include <DSPI.h>
#include <OBCI32_SD.h>
#include <EEPROM.h>
#include <OpenBCI_32bit_Library.h>
#include <OpenBCI_32Bit_Library_Definitions.h>

boolean addAccelToSD = false; // On writeDataToSDcard() call adds Accel data to SD card write
boolean addAuxToSD = false; // On writeDataToSDCard() call adds Aux data to SD card write
boolean SDfileOpen = false;
int stand;
int target;

////
void setup() {
  // Bring up the OpenBCI Board
  board.begin();
  //startFromScratch();
  board.useAccel(false);

}

void loop() {

  if (board.streaming) {
    if (board.channelDataAvailable) {
      // Read from the ADS(s), store data, set channelDataAvailable flag to false
      board.updateChannelData();

      board.auxData[0] = 0;
      board.auxData[1] = 0;
      board.auxData[2] = 0;
             
      stand = digitalRead(17);
      target = digitalRead(12);
        
      // Read standard stimuli
      if (stand == HIGH) {

        board.auxData[0] = 0x6220; // D11
        board.auxData[1] = 0;      // D12
        board.auxData[2] = 0;      // D17                              
       }     

      // Read target stimuli
      if (target == HIGH) {

        board.auxData[0] = 0;
        board.auxData[1] = 0x6220;
        board.auxData[2] = 0;        
      }
 
   // Send packet with channel data and auxData contents
      board.sendChannelData();   
    }
  }

  // Check the serial port for new data
  if (board.hasDataSerial0()) {
    // Read one char from the serial port
    char newChar = board.getCharSerial0();

    // Send to the board library
    board.processChar(newChar);
  }
  board.loop();
}
