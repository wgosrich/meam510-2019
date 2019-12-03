/************************************************************
* HAT code
* This code recieves game and health information from a central control center over TCP.
* It also acts as an SPI slave to present that information.
*
* IP Address of top hat is (100 + robotNumber)
*
* SPI information requests
*   0 Game Info, Bit: 4 SyncStatus,  3 CooldownStatus, 2 AutonomousMode, 1 Reset, 0 GameStatus
*   1 Nexus 1 LSB 1 Byte
*   2 Nexus 1 MSB 2 Bits
*   3 Nexus 2 LSB 1 Byte
*   4 Nexus 2 MSB 2 Bits
*   5-12 Robot 0-7 respectivly
*   13 Tower Status low Nyble is bottom tower status, high nyble is top tower status
*
* IO
*   Weapon  32
*   Button  23
*
*   SCL   25
*   SDA   33
*
*   DIP 0 2
*   DIP 1 4
*   DIP 2 16
*   DIP 3 17
*   DIP 4 22
*   DIP 5 18
*   DIP 6 19
*   DIP 7 21
*
*
* V1: This just recieves the TCP information and parses it
*     to game and health info.  If more than one byte is
*     sent in the packet it just uses the last one.
*
* V2: This adds in the code to make the ESP32 act as a spi slave.
*
*
* V3: The TCP and UDP comunication done.  Spi not in yet.
*
* V4: V3 with the io Buttons added.
*
* V5: V4 but the SPI Stuff added
* V5_1:V5 11/5 Diego separating the UDP response port look for !!!!!! or Diego
*
* V6:  Started adding in the SPI but we decided to go with I2C so it was skipped
*
* V7:  Added in UDP Sync Beacon at startup, once a TCP message is sent requesting a sync it moves on.  Changed to receive on UDP and send on TCP.  Included I2C test communication to make sure it didn't break anything
*       TODO:  Work out I2C message types.  Need a request bytes and write for healing frequency.
*
* V8:  Formated the I2C to be properly formatted.
*
*
************************************************************/

#include <WiFi.h>
#include <WiFiUdp.h>
#include "esp_system.h"
//LED STUFF++++++++++++++++++++++++++++++++++++++++
#include "FastLED.h"
FASTLED_USING_NAMESPACE

#if defined(FASTLED_VERSION) && (FASTLED_VERSION < 3001000)
#warning "Requires FastLED 3.1 or later; check github for latest code."
#endif

#define RED 0xFF0000          // color for the red team
#define BLUE 0x0000FF         // color for the blue team
#define TEAMCOLOR RED
#define HEALTHCOLOR 0x00FF00  // color for the health LEDs
#define FULLHEALTH 1000
#define FLASHHALFPERIOD 250   // the blue team is supposed to flash this is half of the period of that flash

#define DATA_PIN    12  //What pin is the LED ring data on
#define LED_TYPE    WS2812  //APA102
#define COLOR_ORDER GRB  // changes the order so we can use standard RGB for the values we set.
#define NUM_LEDS    72  //Number of LEDs in the ring
CRGB leds[NUM_LEDS];  // this is the place you set the value of the LEDs each LED is 24 bits

#define BRIGHTNESS          60   // lower the brighness a bit so it doesn't look blown out on the camera.
#define FRAMES_PER_SECOND  120   // some number this is likely faster than needed

// -- The core to run FastLED.show()
#define FASTLED_SHOW_CORE 0

// -- Task handles for use in the notifications
static TaskHandle_t FastLEDshowTaskHandle = 0;
static TaskHandle_t userTaskHandle = 0;
//END LED STUFF++++++++++++++++++++++++++++++++++++++++



#define LEDBUILTIN 2

#define ROBOTID0 27


#define BUTTON 33
#define WEAPON 13

//#define SCL 14  // not used but kept in for consistency with towers
//#define SDA 12

// byte for saying what happened
#define NOTHINGHAPPENED 0
#define WASHIT 1
#define MADEHIT 2
#define HEALING 3

#define INCOMINGMESSAGESIZE 128

const char* ssid     = "AslamahFi";
const char* password = "finewhatever";


#define EVENTDELAY 300 // delay this many ms after the button or weapon is used before it can change again
const int udpSyncPort = 3333;
const int TCPSyncPort = udpSyncPort; // !!!!! 11/5 Diego separating the UDP response port
const int TCPSendPort = 4444;
const int udpReceivePort = 5555;

IPAddress centralIP(192,168,43,186);  //IP address for central.  Changing this in the code appears to only change it locally.
byte robotNumber;

volatile bool buttonPressedFlag = 0;

volatile unsigned long buttonPressedTime = 0;

volatile unsigned long syncTimeUsed = 0;        // Records when sync happens so we can subract out the time
volatile unsigned long syncTime = 0;        // Records when sync happens so we can subract out the time

byte incomingData[INCOMINGMESSAGESIZE];

portMUX_TYPE mux = portMUX_INITIALIZER_UNLOCKED;  // needed for interrupts.


//WiFiServer serverSend(TCPSendPort); // Set the server for sending out messages. I don't think this is used anymore, CHECK THEN COMMENT OUT.
WiFiClient cli;  //  Setup up a wifi client to open communication with the main server.  This is why we don't need serverSend.

WiFiUDP udpReceive; // Set the server for listening for messages
WiFiUDP udpSync;


// Interupt handlers for the button and weapon
void IRAM_ATTR handleButtonInterrupt() {
  portENTER_CRITICAL_ISR(&mux);
    if((millis()-syncTime)>(buttonPressedTime+EVENTDELAY)){// if it has been more than the delay you can assume it is another hit.  It is not clear if this was a bouncing issue or with how the interrupts were handled, but this accounts for either.
      buttonPressedTime = millis()-syncTime; // Set the time the button was pressed.
      buttonPressedFlag = 1;  // Set the flag so we know to send a message
      //Serial.print("button pressed at ");
      //Serial.println(buttonPressedTime);
    }
  portEXIT_CRITICAL_ISR(&mux);
}


//LED STUFF++++++++++++++++++++++++++++++++++++++++
/** show() for ESP32
 *  Call this function instead of FastLED.show(). It signals core 0 to issue a show,
 *  then waits for a notification that it is done.
 */
void FastLEDshowESP32()
{
    if (userTaskHandle == 0) {
        // -- Store the handle of the current task, so that the show task can
        //    notify it when it's done
        userTaskHandle = xTaskGetCurrentTaskHandle();

        // -- Trigger the show task
        xTaskNotifyGive(FastLEDshowTaskHandle);

        // -- Wait to be notified that it's done
        const TickType_t xMaxBlockTime = pdMS_TO_TICKS( 200 );
        ulTaskNotifyTake(pdTRUE, xMaxBlockTime);
        userTaskHandle = 0;
    }
}

/** show Task
 *  This function runs on core 0 and just waits for requests to call FastLED.show()
 */
void FastLEDshowTask(void *pvParameters)
{
    // -- Run forever...
    for(;;) {
        // -- Wait for the trigger
        ulTaskNotifyTake(pdTRUE, portMAX_DELAY);

        // -- Do the show (synchronously)
        FastLED.show();

        // -- Notify the calling task
        xTaskNotifyGive(userTaskHandle);
    }
}

void SetupFastLED(void){
  // tell FastLED about the LED strip configuration
  FastLED.addLeds<LED_TYPE,DATA_PIN,COLOR_ORDER>(leds, NUM_LEDS).setCorrection(TypicalLEDStrip);

  // set master brightness control
  FastLED.setBrightness(BRIGHTNESS);

  int core = xPortGetCoreID();
    Serial.print("Main code running on core ");
    Serial.println(core);

    // -- Create the FastLED show task
    xTaskCreatePinnedToCore(FastLEDshowTask, "FastLEDshowTask", 2048, NULL, 2, &FastLEDshowTaskHandle, FASTLED_SHOW_CORE);

}


void ShowHealth(int health){
  //int healthLeds[] = {1,2,3,4,5,7,8,9,10,11,13,14,15,16,17,19,20,21,22,23}; // the location of the 24 LEDs used for health
  //int teamColor = RED*digitalRead(ROBOTID0)+BLUE*!digitalRead(ROBOTID0);
  int teamColor = TEAMCOLOR;
  leds[0] = teamColor*(health > 0);  // last LED doesn't go off till the health is 0
  leds[NUM_LEDS-1] = teamColor*(health == FULLHEALTH);  // last LED doesn't go off till the health is 0
  for(int i=1; i<NUM_LEDS-1; i++){
    leds[i] = teamColor*(health > (i*FULLHEALTH/NUM_LEDS));  // the other leds go off in increments of 5
  }


}

void clearLEDs(void){
  for(int i=0; i<NUM_LEDS; i++){
    leds[i] = 0; // Turn off everything
  }
}
// END LED STUFF++++++++++++++++++++++++++++++++++++++++

//%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
//WDT

const int wdtTimeout = 10000;  //time in ms to trigger the watchdog
hw_timer_t *timer = NULL;

void IRAM_ATTR resetModule() {
  ets_printf("Our Watchdog Reboot\n");
  esp_restart();
}

void wdtInit(void){
  timer = timerBegin(0, 80, true);                  //timer 0, div 80
  timerAttachInterrupt(timer, &resetModule, true);  //attach callback
  timerAlarmWrite(timer, wdtTimeout * 1000, false); //set time in us
  timerAlarmEnable(timer);                          //enable interrupt
}
// WDT end
//%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


void setup() {
  Serial.begin(115200);

  // setup pins
  pinMode(ROBOTID0,INPUT_PULLUP);


  pinMode(BUTTON,INPUT_PULLUP);

  pinMode(LEDBUILTIN,OUTPUT);

  //Create interups for weapon and button
  attachInterrupt(digitalPinToInterrupt(BUTTON), handleButtonInterrupt, FALLING);

    // setup robot number
  //robotNumber=(80);//+digitalRead(ROBOTID0));
  robotNumber=(80+(TEAMCOLOR==BLUE));
  Serial.print("Robot Number: ");
  Serial.println(robotNumber);
  Serial.println();

  IPAddress myIPaddress(192, 168, 43, (robotNumber)); // arbitrary address need to send to

  Serial.print("Connecting to ");
  Serial.println(ssid);

  // Connect to the WiFi
  WiFi.begin(ssid, password);
  WiFi.config(myIPaddress, IPAddress(192, 168, 1, 1), IPAddress(255, 255, 255, 0));

  // Wait for connection
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("WiFi connected");

//  udpSync.begin(udpSyncPort);
//  udpReceive.begin(udpReceivePort);
//
//  // Sync Beacon.  This sends a Sync response with number 0 to Central to let it know that we just rebooted and need to sync.
//  char syncPacket[] = {0, robotNumber};
//  //cli = serverSend.available();
//  bool messageSent = 0;
//  while (!messageSent){
//    delay(100);
//    Serial.println("I need to sync!");
//    cli.connect(centralIP,TCPSyncPort);//!!!!!!!!!    11/5 Diego
//    if (cli) {
//      cli.print(syncPacket);
//      Serial.println("Sync Response sent");
//      messageSent = 1;
//      //serverSend.write(syncPacket,sizeof(syncPacket)); //(data bytes to send, number of bytes of the data)
//    }
//
//  }

  //LED STUFF++++++++++++++++++++++++++++++++++++++++
  SetupFastLED();  // Setup the LEDs
  //END LED STUFF++++++++++++++++++++++++++++++++++++++++

  wdtInit();  // need to init at the end or it will reset on one missed message
  udpReceive.begin(udpReceivePort);

  Serial.println("End of Setup");

}

void loop() {

   timerWrite(timer, 0); //reset timer (feed watchdog)


   static bool gameStatus = 0;              // game on 1, game off 0
   static bool reset = 0;                   // 1 for reseting, not sure what the intention is here, check with Diego
   static bool autoMode = 0;                // 0 not autonomous, 1 is autonomous

   // (Removed - 5 Nov 2019 - Aslamah)
   // static bool syncStatus = 0;
   // static bool syncStatusPrev = syncStatus;              // 0 sync still hasn't happend, 1 sync has happend
  // 0 sync still hasn't happend, 1 sync has happend
   static byte coolDownStatus = 0;          // 0 ready to hit, 1 cooling down

   static byte healthRobot[8];      // health of each robot as a byte
   static byte healthNexus[4];      // health of the two nexi each is 10 bit
   static byte towerStatus[2];      // status of the two towers.  Not sure why this needs 4 bits each.


   //static unsigned int incomingDataAddress= incomingData;
   static int packetNumber = 0;  // Used to track if a new packet has come in
   static int packetNumberOld;  // Used to track if a new packet has come in

  char packetBuffer[2]; //buffer to hold incoming packet

   packetNumberOld = packetNumber;
   //packetNumber = handleTCPserver(incomingDataAddress);
  //Serial.println("1");
  // If something happened send that info

//  Aslamah test
  static int time_old = millis();
  if(millis() - time_old >= 1000) {
    buttonPressedFlag = true;
    sendButtonPress();
    time_old = millis();
  }
  //Serial.println("2");



  // -----------------------------------------------------------------
  // Changed to reading from udp
  int packetSize = udpReceive.parsePacket();
  if (packetSize) {
    digitalWrite(LEDBUILTIN,!digitalRead(LEDBUILTIN));

    Serial.print("Received packet of size ");
    Serial.println(packetSize);
    Serial.print("From ");
    //IPAddress centralIP = udpSync.remoteIP();
    Serial.print(centralIP);
    Serial.print(", port ");
    Serial.println(udpReceive.remotePort());

    // read the packet into packetBufffer
    int len = udpReceive.read(incomingData, 200);
    if (len > 0) {
      packetBuffer[len] = 0;
    }
//    Serial.println("Contents:");
//    for(int i=0; i<len; i++) {
//      Serial.println(incomingData[i]);
//    }
    packetNumber++;
    udpReceive.flush();

  }

  // -----------------------------------------------------------------


//==========================================================================================================
// Sync with UDP
// (Removed - 5 Nov 2019 - Aslamah)
  // if ((syncTime == 0) | ~syncStatus) {
  //   //read udp
  //   int packetSize = udpSync.parsePacket();
  //   if (packetSize) {
  //
  //     syncTime=millis(); // if you get a packet the sync get the offset for syncing
  //
  //     Serial.print("Received packet of size ");
  //     Serial.println(packetSize);
  //     Serial.print("From ");
  //     //IPAddress centralIP = udpSync.remoteIP();
  //     Serial.print(centralIP);
  //     Serial.print(", port ");
  //     Serial.println(udpSync.remotePort());
  //
  //     // read the packet into packetBufffer
  //     int len = udpSync.read(packetBuffer, 2);
  //     if (len > 0) {
  //       packetBuffer[len] = 0;
  //     }
  //     Serial.println("Contents:");
  //     Serial.println((byte)packetBuffer[0]);
  //
  //     byte udpPacketNumber = packetBuffer[0]; // the number of the sync packet sent, specific to how we are organizing things.
  //
  //     // send the TCP response
  //     char syncPacket[] = {robotNumber, udpPacketNumber};
  //     //cli = serverSend.available();
  //     cli.connect(centralIP,TCPSyncPort);//!!!!!!!!!    11/5 Diego
  //     if (cli) {
  //       cli.print(syncPacket);
  //       Serial.println("Sync Response sent");
  //       //serverSend.write(syncPacket,sizeof(syncPacket)); //(data bytes to send, number of bytes of the data)
  //     }
  //     cli.stop();
  //     Serial.print("Robot Number: ");
  //     Serial.println(robotNumber);
  //     //Serial.println();
  //     Serial.print("syncTime: ");
  //     Serial.println(syncTime);
  //     Serial.println();
  //
  //   }
  // }
  //
  //
  // if (syncStatus > syncStatusPrev){
  //   syncTimeUsed = syncTime;
  // }
  // syncStatusPrev = syncStatus;

   //-----------------------------------------------------------------------------------------------------
   // Parse Data
   delay(1);
   // Parse the data if something new came in.  This is not required as we can just have them request a byte from the incomingData
   if (packetNumber-packetNumberOld){ // a new packet came in update info.



      gameStatus = 1 & (incomingData[0]>>0);      // game on 1, game off 0
      reset = 1 & (incomingData[0]>>1);           // 1 for reseting, not sure what the intention is here, check with Diego
      autoMode = 1 & (incomingData[0]>>2);        // 0 not autonomous, 1 is autonomous
      // (Removed - 5 Nov 2019 - Aslamah)
      // syncStatus = 1 & (incomingData[0]>>3);      // 0 sync still hasn't happend, 1 sync has happend
      // Serial.print("Sync Status: ");
      // Serial.println(syncStatus);
      // Serial.println();
      // coolDownStatus = incomingData[1];  // 0 ready to hit, 1 cooling down // (Removed - 5 Nov 2019 - Aslamah)
      // healthNexus[0] = incomingData[2];
      // healthNexus[1] = incomingData[3];
      // healthNexus[2] = incomingData[4];
      // healthNexus[3] = incomingData[5]; // (Removed - 5 Nov 2019 - Aslamah)

      healthNexus[0] = incomingData[1];
      healthNexus[1] = incomingData[2];
      healthNexus[2] = incomingData[3];
      healthNexus[3] = incomingData[4];

      // healthRobot[0] = incomingData[6];
      // healthRobot[1] = incomingData[7];
      // healthRobot[2] = incomingData[8];
      // healthRobot[3] = incomingData[9];
      //

      // (Removed - 5 Nov 2019 - Aslamah)
      // healthRobot[4] = incomingData[10];
      // healthRobot[5] = incomingData[11];
      // healthRobot[6] = incomingData[12];
      // healthRobot[7] = incomingData[13];

      // (Removed - 5 Nov 2019 - Aslamah)
      // towerStatus[1] = 0x0F & (incomingData[14]>>0);      // This can be cleaned up because you just need the and for the first one and the shift for the second but I like the consistency.
      // towerStatus[2] = 0x0F & (incomingData[14]>>4);
   }

  // (Removed - 3 Dec - Aslamah)
//    if(reset){
//      ESP.restart();
//    }

   // end parse
   //------------------------------------------------------------------------

  static int health;

  if (TEAMCOLOR == RED){ //red
    health = (healthNexus[0] | (healthNexus[1]<<8));
  }
  else{
    health = (healthNexus [2] | (healthNexus[3]<<8));
  }
  ShowHealth(health); //set the LEDs for the health

  Serial.print("health: ");
  Serial.println(health);

  delay(FLASHHALFPERIOD/2);  // wait a bit so the LEDs don't cycle too fast
  FastLEDshowESP32(); //Actually send the values to the ring

  FastLED.delay(1000/FRAMES_PER_SECOND); // insert a delay to keep the framerate modest
}


void sendButtonPress(){
  // send the TCP packet when button pressed
      if(buttonPressedFlag){
        //char packet[] = {WASHIT, buttonPressedTime, buttonPressedTime>>(8*1), buttonPressedTime>>(8*2), buttonPressedTime>>(8*3)}; // (Removed - 5 Nov 2019 - Aslamah)
        char packet[] = {WASHIT}; // (Added - 5 Nov 2019 - Aslamah)
        buttonPressedFlag = 0;  //clear flag
        Serial.println(buttonPressedTime);
        //cli = serverSend.available();
        Serial.println("trying to send");
        Serial.println(centralIP);
        cli.connect(centralIP,TCPSendPort);
        if (cli) {
          //cli.print(packet);
          cli.write(packet,sizeof(packet));
          Serial.println("I said I was hit");
          //serverSend.write(syncPacket,sizeof(syncPacket)); //(data bytes to send, number of bytes of the data)
        }
        cli.stop();
      }
}
