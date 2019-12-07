/* Based on WebSocketServer_LEDcontrol.ino  Created on: 26.11.2015 From: http://arduino-er.blogspot.com/2016/05/nodemcuesp8266-implement.html
 *
 *  Updated 2016/07/12 By: Paul Stegall
 *  Reads in button and switch infromation and displays values on a led bar, wiring can be found in JudgeBoardV2.svg
 *  Websockets not currently utilized.
 *
 *  https://github.com/Links2004/arduinoWebSockets
 *
 */
//Modified to act as AP
//arduino-er.blogspot.com

//#include <Arduino.h>

//#include <ESP8266WiFi.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include "esp_system.h"
//#include <ESP8266WiFiMulti.h>
//#include <WebSocketsClient.h>
//#include <ESP8266WebServer.h>
//#include <ESP8266mDNS.h>
//#include <Hash.h>
// ********** LED STUFF ********** //
//#define FASTLED_ESP8266_RAW_PIN_ORDER
#include "FastLED.h"

// How many leds in your strip?
#define NUM_LEDS 23
#define DATA_PIN 12
#define CLOCK_PIN 27

// Define the array of leds
CRGB leds[NUM_LEDS];
// **********  MACROS  ********** //

#define MIN(X, Y)  ((X) < (Y) ? (X) : (Y))
#define MAX(X, Y)  ((X) > (Y) ? (X) : (Y))
#define SGN(X)     ((X > 0) - (X < 0))

//#define HIT_BUTTON1   D6
//#define HIT_BUTTON2   D7
//#define TOWER_SELECT D5

#define HIT_BUTTON1   25
#define HIT_BUTTON2   26
#define TOWER_SELECT 33

#define USE_SERIAL Serial
#define RED_B  1
#define BLUE_B 0

//TUNING PARAMETERS
//*********************************************************
#define TOWER_SWITCH_PER  2000     //milliseconds after capture before which the opposing team can recapture
#define COOLDOWN_TIME     3000     //milliseconds before uncontested tower starts to reduce to zero
#define HIT_SEND_PER      1000       //milliseconds between hit sends
#define DOWN_MULTI        3        //how many times faster gauge drops when the opposing team presses the button
#define GAUGE_MAX         8000     //milliseconds to fill gauge and capture tower

// Boolean, disables controlling teams button, NERFING defense causes PINGPONGing (comment to disable)
#define NERF_DEFENSE()    //if (towerState!=0){ buttonSt[abs(towerState-1) / 2] = 0; }
//NERFS Defense by allowing them to pause the gauge but not to affect the value
#define HOLD_NO_DROP()    ((teamDir*towerState) !=1)

// byte for saying what happened
#define NOTHINGHAPPENED 0
#define WASHIT 1
#define MADEHIT 2
#define HEALING 3

#define INCOMINGMESSAGESIZE 128

//*********************************************************


const char* ssid     = "TestCentral";
const char* password = "r0b0tics";

const int TCPSendPort = 4444;
const int udpReceivePort = 5555;

IPAddress centralIP(192,168,1,2);  //IP address for central.  Changing this in the code appears to only change it locally.
//IPAddress centralIP(10, 103, 213, 225); //IP address for central.  Changing this in the code appears to only change it locally.


// Tower gauge parameters
int towerGauge = 0;
int towerState = 0;//-1 is BLUE, 1 is RED

// Communication string
char hitString [7];


byte incomingData[INCOMINGMESSAGESIZE];
WiFiClient cli;  //  Setup up a wifi client to open communication with the main server.  This is why we don't need serverSend.
WiFiUDP udpReceive; // Set the server for listening for messages


void setup() {
    //USE_SERIAL.begin(921600);
    USE_SERIAL.begin(115200);

    //USE_SERIAL.setDebugOutput(true);

    USE_SERIAL.println();
    USE_SERIAL.println();
    delay(1000);

    pinMode(HIT_BUTTON1, INPUT_PULLUP);
    pinMode(HIT_BUTTON2, INPUT_PULLUP);
    pinMode(TOWER_SELECT, INPUT_PULLUP);
    pinMode(LED_BUILTIN, OUTPUT);
    FastLED.addLeds<APA102, DATA_PIN, CLOCK_PIN, BGR>(leds, NUM_LEDS);
    
    digitalWrite(LED_BUILTIN, LOW);
    
    //IPAddress myIPaddress(192, 168, 1, 98+digitalRead(TOWER_SELECT));
    IPAddress myIPaddress(192, 168, 1, 99);
    
    WiFi.config(myIPaddress, IPAddress(192, 168, 1, 1), IPAddress(255, 255, 255, 0)); 
    WiFi.begin(ssid, password);
    

    // Wait for connection
  while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
  }
  Serial.println("WiFi connected");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  udpReceive.begin(udpReceivePort);


}

void loop() {
  static bool gameStatus = 0;              // game on 1, game off 0
  static bool reset = 0;                   // 1 for reseting, not sure what the intention is here, check with Diego
  static bool autoMode = 0;                // 0 not autonomous, 1 is autonomous

  static bool syncStatus = 0;              // 0 sync still hasn't happend, 1 sync has happend
  static byte coolDownStatus = 0;          // 0 ready to hit, 1 cooling down

  static byte healthRobot[8];      // health of each robot as a byte
  static byte healthNexus[4];      // health of the two nexi each is 10 bit
  static byte towerStatus[2];      // status of the two towers.  Not sure why this needs 4 bits each.


  //static unsigned int incomingDataAddress= incomingData;
  static int packetNumber = 0;  // Used to track if a new packet has come in
  static int packetNumberOld;  // Used to track if a new packet has come in

  // char packetBuffer[2]; //buffer to hold incoming packet

  packetNumberOld = packetNumber;

  // -----------------------------------------------------------------
  // Changed to reading from udp
  //Serial.println("384");
  int packetSize = udpReceive.parsePacket();
  if (packetSize) {
    digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
    Serial.print("Received packet of size ");
    Serial.println(packetSize);
    Serial.print("From ");
    //IPAddress centralIP = udpSync.remoteIP();
    Serial.print(centralIP);
    Serial.print(", port ");
    Serial.println(udpReceive.remotePort());
    //Serial.println("395");
    // read the packet into packetBufffer
    int len = udpReceive.read(incomingData, 200);
    if (len > 0) {
      incomingData[len] = 0;
    }
//    Serial.println("Contents:");
//    for (int i = 0; i < len; i++) {
//      Serial.println(incomingData[i]);
//    }
    packetNumber++;
    udpReceive.flush();
    //Serial.println("407");
  }

  // -----------------------------------------------------------------
  //-----------------------------------------------------------------------------------------------------
  // Parse Data
  delay(1);
  // Parse the data if something new came in.  This is not required as we can just have them request a byte from the incomingData
  if (packetNumber - packetNumberOld) { // a new packet came in update info.
    //Serial.println("487");


    gameStatus = 1 & (incomingData[0] >> 0);    // game on 1, game off 0
    reset = 1 & (incomingData[0] >> 1);         // 1 for reseting, not sure what the intention is here, check with Diego
    autoMode = 1 & (incomingData[0] >> 2);      // 0 not autonomous, 1 is autonomous
    syncStatus = 1 & (incomingData[0] >> 3);    // 0 sync still hasn't happend, 1 sync has happend
    Serial.print("Game Status: ");
    Serial.println(gameStatus);
    Serial.println();
//    Serial.print("Sync Status: ");
//    Serial.println(syncStatus);
//    Serial.println();
    //(removed - 12/2/19 - walker)
    // shouldn't need this info
    /*
    coolDownStatus = incomingData[1];  // 0 ready to hit, 1 cooling down
    healthNexus[0] = incomingData[2];
    healthNexus[1] = incomingData[3];
    healthNexus[2] = incomingData[4];
    healthNexus[3] = incomingData[5];

    healthRobot[0] = incomingData[6];
    healthRobot[1] = incomingData[7];
    healthRobot[2] = incomingData[8];
    healthRobot[3] = incomingData[9];

    healthRobot[4] = incomingData[10];
    healthRobot[5] = incomingData[11];
    healthRobot[6] = incomingData[12];
    healthRobot[7] = incomingData[13];
    */

    towerStatus[1] = 0x0F & (incomingData[14] >> 0);    // This can be cleaned up because you just need the and for the first one and the shift for the second but I like the consistency.
    towerStatus[2] = 0x0F & (incomingData[14] >> 4);
  }

  if (reset) {
    ESP.restart();
  }

  // end parse
  //------------------------------------------------------------------------


  //Run LED strip
  if(gameStatus){
    tower_handle();  //Counts up and updates the towerGauge and towerState
    tower_send();      
  }
  linear_growth(towerGauge/(GAUGE_MAX/100), towerState, leds);
  FastLED.show();
//    tower_send();
  delay(50);  // wait a bit
}
//**********************************
//TOWER_SEND()
void tower_send(){

    // Hit timing static
    static unsigned long sentTime  = 0;
    //if (towerState == 0) return;
    //Send damage information to central
    if (millis()-sentTime > HIT_SEND_PER){ //if time since last send is greater than 1 sec
        sentTime = millis();
        //Shift tower gauge by 127 and send
        byte towerValue = towerGauge/(GAUGE_MAX/100)+127;  //Shift the +- percent to an always + value
        Serial.print("Tower Value: ");
        Serial.println(towerValue);


        // packet = [2*istowercaptured]
        // char packet[] = {((MADEHIT * abs(towerState)) | ((towerState==1)<<4)|(1<<7)), towerValue};(removed- 12/2/19 - walker) // the one in the 8th bit is just so the first byte is not zero
        char packet[] = {(abs(towerState)) | (((!(towerState==1))<<1)|(1<<7))}; //(added - 12/2/19 - walker)
      //cli = serverSend.available();
      Serial.println("trying to send");
      Serial.println(centralIP);
      cli.connect(centralIP, TCPSendPort);
      if (cli) {
        //cli.print(packet);
        cli.write(packet, sizeof(packet));
        Serial.println("PowPow");
        //serverSend.write(syncPacket,sizeof(syncPacket)); //(data bytes to send, number of bytes of the data)
      }
      cli.stop();
          
    }
//  yield();
}

//**********************************
//TOWER_HANDLE()
void tower_handle() {
    // Static time variables for handling how the tower is captured.
    static unsigned long        timeLast  = millis();
    static unsigned long  towerSwitchTime = -TOWER_SWITCH_PER;
    static unsigned long    cooldownTime  = millis();
    static unsigned int    cooldownFlag  = 0;
    // Save button states, negated because of pullups
    int buttonSt[2] = {!digitalRead(HIT_BUTTON1),!digitalRead(HIT_BUTTON2)};

    Serial.println("Tower Handle:");
    //NERF_DEFENSE(); (removed - 12/2/19 - walker)

    int timePast = millis()-timeLast;
    timeLast = millis();
    Serial.println(buttonSt[RED_B]);
    Serial.println(buttonSt[BLUE_B]);
    // If both buttons are pressed, nothing happens
    if (buttonSt[RED_B]&&buttonSt[BLUE_B]) return;

//    Serial.println("Tower Handle:3");
    // If the tower just switched, ignore inputs for TOWER_SWITCH_PER ms
    if (millis() - towerSwitchTime < TOWER_SWITCH_PER) return; //??? not sure what this does -- asks if the current time plus 1000 is less than 1000?

    Serial.println("Tower Handle:4");
    // Change in gauge sign/direction
    /* teamDir = 1 if red is pressed, -1 if blue is pressed,
     *           0 if neither is pressed, 0 if both are pressed (handled above)*/
    int teamDir = (buttonSt[RED_B]-buttonSt[BLUE_B]); 

    // If only one button is pressed
    /* Many of the operations below use the sign of the towerGauge and teamDir to make decisions about state
     * (I think I over did this, should be moved back to if or switch statement, I just hate repeating code.-Diego)*/
    if (teamDir && HOLD_NO_DROP()){

        // Check if opposing team from current button press partially captured the tower
        if (towerGauge * teamDir < 0){
            /* Negative implies that the towerGauge was pushed partially by the other team
             * since otherwise signs would match and cancel.
             * If this is the case, we multiply the tower rate by DOWN_MULTI
             * allowing a team to quickly clear the opposing teams partial capture
             * to facilitate their capture. This does not go past zero in this mode.*/
            towerGauge += DOWN_MULTI * teamDir * timePast;
            towerGauge = teamDir * MIN( teamDir * towerGauge, 0);
        }else{
            /*Normal capture counts the millis the team holds the button in towerGauge */
            towerGauge += teamDir * timePast;
        }
        //Clears the cooldown flag if any button is pressed
        cooldownFlag = 0;
    }
    /* If neither button is being pressed but the gauge is partially engaged,
     * start a cooldown timer after which the tower will drop back down to zero.*/
    else if(towerGauge != 0){
        //Start timer.
        if(!cooldownFlag){
            cooldownFlag = 1;
            cooldownTime = millis();
        }
        //If timer is up, lower the towerGauge at the normal 1/ms
        else if(millis()-cooldownTime > COOLDOWN_TIME){
            towerGauge = timePast > abs(towerGauge) ? 0 : towerGauge-(SGN(towerGauge)*timePast) ;
        }
    }
    // If towerGauge reaches max, set tower capture by that team
    if (abs(towerGauge) >= GAUGE_MAX){
        towerSwitchTime = millis();
        towerState = SGN(towerGauge); //1 for RED
    }
    /* Clamp towerGauge to 0 for current captors,
     * but allow gauge to move for attackers */
    towerGauge = (!(towerState*towerGauge > 0)) * towerGauge;


   USE_SERIAL.print("\tRed Button: \t");
   USE_SERIAL.print(buttonSt[RED_B]);
   USE_SERIAL.print("\tBlue Button: \t");
   USE_SERIAL.println(buttonSt[BLUE_B]);
   USE_SERIAL.print("Tower Gauge: \t");
   USE_SERIAL.println(towerGauge);
   USE_SERIAL.print("\tTime Past: \t");
   USE_SERIAL.println(timePast);
}

//**********************************
//LINEAR_GROWTH()
//  INPUTS:
//  percentage: -100 <= percentage <= 100
//       state:  1 for red capture or -1 for blue capture
//        leds: LED array
void linear_growth(int percentage, int state, CRGB leds[] ){
    /* These probably don't need to be static,
     * but should be a tiny bit faster in exchange for some memory usage.*/
    static byte maxBrightness = 255;
    static byte      saturate = .5 * maxBrightness;
    static byte         slope = .1 * maxBrightness;
    static int         growth = saturate + NUM_LEDS * slope;

    uint8_t i = 0;
    int value;

    /* Percentage should be an integer in [-100,100], the sign gives
     * us whether this is red or blue team capturing (1 for red, -1 for blue)*/
    int8_t redOrBlue = (percentage > 0) - (percentage < 0);

    percentage = abs(percentage);

    // Which color? 0 is red, 160 is blue
    uint8_t hue = (redOrBlue < 0) * 160;
    // Which background color?
    uint8_t bgHue = (state < 0) * 160;


    for(i=0;i<NUM_LEDS;i++){
        // CHSV( HUE, SATURATION, VALUE);
        // value is a linear function: value = m x + b
        // but it also handles whether the leds should be blue or red and
        // the switch in direction that comes with that.
        // the constant slope, m =  (- redOrBlue *slope)
        // The intercept,b, depends on the percentage
        // w/ b =( growth * percentage) / 100 - slope * NUM_LEDS*(redOrBlue<0)
        value = (- redOrBlue *slope) * i
              + (growth * percentage) / 100 - slope * NUM_LEDS*(redOrBlue<0) ;
        leds[i] =  CHSV( hue, 255 , MIN( MAX(value, 0), saturate));
        if(state!=0){
            leds[i]  += CHSV( bgHue, 255 ,MIN( MAX(maxBrightness - value, 0),  maxBrightness)) ;
        }
    }
    if (state!=0){
        cannon_ball(leds,state);
    }

}


//**********************************
//CANNON_BALL()
void cannon_ball( CRGB leds[] , int dir){
    static unsigned long cannonTime = millis();
    static uint8_t cannonRate = NUM_LEDS; //# of LEDs traversed per second

    int cannonBallLoc = (dir<0)*(NUM_LEDS-1) + dir *( ((millis()-cannonTime)*cannonRate)/1000);// time * leds per millisecond

    //Deal with cannonball reset
    if ( (cannonBallLoc >= NUM_LEDS) || (cannonBallLoc < 0) ){
      cannonTime = millis();
      cannonBallLoc = (dir<0) * (NUM_LEDS-1);
    }
    leds[cannonBallLoc]=CHSV(0,0,255); //The cannon ball is WHITE
}
