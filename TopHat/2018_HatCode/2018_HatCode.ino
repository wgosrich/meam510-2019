/************************************************************
  HAT code
  This code recieves game and health information from a central control center over TCP.
  It also acts as an SPI slave to present that information.

  IP Address of top hat is (100 + robotNumber)

  SPI information requests
    0 Game Info, Bit: 4 SyncStatus,  3 CooldownStatus, 2 AutonomousMode, 1 Reset, 0 GameStatus
    1 Nexus 1 LSB 1 Byte
    2 Nexus 1 MSB 2 Bits
    3 Nexus 2 LSB 1 Byte
    4 Nexus 2 MSB 2 Bits
    5-12 Robot 0-7 respectivly
    13 Tower Status low Nyble is bottom tower status, high nyble is top tower status

  IO
    Weapon  32
    Button  23

    SCL   25
    SDA   33

    DIP 0 2
    DIP 1 4
    DIP 2 16
    DIP 3 17
    DIP 4 22
    DIP 5 18
    DIP 6 19
    DIP 7 21


  V1: This just recieves the TCP information and parses it
      to game and health info.  If more than one byte is
      sent in the packet it just uses the last one.

  V2: This adds in the code to make the ESP32 act as a spi slave.


  V3: The TCP and UDP comunication done.  Spi not in yet.

  V4: V3 with the io Buttons added.

  V5: V4 but the SPI Stuff added
  V5_1:V5 11/5 Diego separating the UDP response port look for !!!!!! or Diego

  V6:  Started adding in the SPI but we decided to go with I2C so it was skipped

  V7:  Added in UDP Sync Beacon at startup, once a TCP message is sent requesting a sync it moves on.  Changed to receive on UDP and send on TCP.  Included I2C test communication to make sure it didn't break anything
        TODO:  Work out I2C message types.  Need a request bytes and write for healing frequency.

  V8:  Formated the I2C to be properly formatted.


************************************************************/

#include <WiFi.h>
#include <WiFiUdp.h>
#include "esp_system.h"
// I2C+++++++++++++++++++++++++++++++++++++++++++++++++++++++

#include <stdio.h>
#include "esp_log.h"
#include "driver/i2c.h"
#include "sdkconfig.h"

#define _I2C_NUMBER(num) I2C_NUM_##num
#define I2C_NUMBER(num) _I2C_NUMBER(num)

#define DATA_LENGTH 128                  /*!< Data buffer length of test buffer */
#define RW_TEST_LENGTH 128               /*!< Data length for r/w test, [0,DATA_LENGTH] */
#define DELAY_TIME_BETWEEN_ITEMS_MS 1000 /*!< delay time between different test items */

#define I2C_SLAVE_SCL_IO (gpio_num_t)33               /*!< gpio number for i2c slave clock */
#define I2C_SLAVE_SDA_IO (gpio_num_t)25               /*!< gpio number for i2c slave data */
#define I2C_SLAVE_NUM I2C_NUMBER(0) /*!< I2C port number for slave dev */
#define I2C_SLAVE_TX_BUF_LEN (2* DATA_LENGTH)              /*!< I2C slave tx buffer size */
#define I2C_SLAVE_RX_BUF_LEN (2 * DATA_LENGTH)              /*!< I2C slave rx buffer size */

#define CONFIG_I2C_SLAVE_ADDRESS 0x28
#define ESP_SLAVE_ADDR CONFIG_I2C_SLAVE_ADDRESS /*!< ESP32 slave address, you can set any 7bit value */

//+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++




#define LEDBUILTIN 2

#define ROBOTID0 4
#define ROBOTID1 16
#define ROBOTID2 17
#define ROBOTID3 22
#define ROBOTID4 18
#define ROBOTID5 19

#define SYNCBEACONPIN 21 //used to bypass the sync beacon so we don't need to change ports when debugging.
//#define ROBOTID7

#define WEAPON 32
#define BUTTON 23

#define SCL 25
#define SDA 33

// byte for saying what happened
#define NOTHINGHAPPENED 0
#define WASHIT 1
#define MADEHIT 2
#define HEALING 3

#define ACCEPTALLTCP 255

#define INCOMINGMESSAGESIZE 128
#define HEALINGDELAY 800 // don't send healing faster than this


//const char* ssid     = "AirPennNet-Device";
//const char* password = "penn1740wifi";

const char* ssid     = "Central";
const char* password = "Y4yR0b0t5";

#define robotTemp 62

#define EVENTDELAY 300 // delay this many ms after the button or weapon is used before it can change again
const int udpSyncPort = 3333;
const int TCPSyncPort = udpSyncPort; // !!!!! 11/5 Diego separating the UDP response port
const int TCPSendPort = 4444;
const int udpReceivePort = 5555;

IPAddress centralIP(192,168,1,2);  //IP address for central.  Changing this in the code appears to only change it locally.
//IPAddress centralIP(10, 103, 213, 225); //IP address for central.  Changing this in the code appears to only change it locally.
byte robotNumber;

volatile bool buttonPressedFlag = 0;
volatile bool weaponPressedFlag = 0;

volatile unsigned long buttonPressedTime = 0;
volatile unsigned long weaponPressedTime = 0;

volatile unsigned long syncTimeUsed = 0;        // Records when sync happens so we can subract out the time
volatile unsigned long syncTime = 0;            // Time when sync message was received.  When the syncMode goes from low to high this becomes the syncTimeUsed


byte incomingData[INCOMINGMESSAGESIZE];
byte packetBuffer[INCOMINGMESSAGESIZE];


portMUX_TYPE mux = portMUX_INITIALIZER_UNLOCKED;  // needed for interrupts.



//WiFiServer serverSend(TCPSendPort); // Set the server for sending out messages. I don't think this is used anymore, CHECK THEN COMMENT OUT.
WiFiClient cli;  //  Setup up a wifi client to open communication with the main server.  This is why we don't need serverSend.


WiFiUDP udpReceive; // Set the server for listening for messages
WiFiUDP udpSync;


String getMacAddress() {
  uint8_t baseMac[6];
  // Get MAC address for WiFi station
  esp_read_mac(baseMac, ESP_MAC_WIFI_STA);
  char baseMacChr[18] = {0};
  sprintf(baseMacChr, "%02X:%02X:%02X:%02X:%02X:%02X", baseMac[0], baseMac[1], baseMac[2], baseMac[3], baseMac[4], baseMac[5]);
  return String(baseMacChr);
}
// Interupt handlers for the button and weapon
void IRAM_ATTR handleButtonInterrupt() {
  portENTER_CRITICAL_ISR(&mux);
  if ((millis() - syncTimeUsed) > (buttonPressedTime + EVENTDELAY)) { // if it has been more than the delay you can assume it is another hit.  It is not clear if this was a bouncing issue or with how the interrupts were handled, but this accounts for either.
    buttonPressedTime = millis() - syncTimeUsed; // Set the time the button was pressed.
    buttonPressedFlag = 1;  // Set the flag so we know to send a message
    //Serial.print("button pressed at ");
    //Serial.println(buttonPressedTime);
  }
  portEXIT_CRITICAL_ISR(&mux);
}

void IRAM_ATTR handleWeaponInterrupt() {
  portENTER_CRITICAL_ISR(&mux);
  if ((millis() - syncTimeUsed) > (weaponPressedTime + EVENTDELAY)) { // if it has been more than the delay you can assume it is another hit.  It is not clear if this was a bouncing issue or with how the interrupts were handled, but this accounts for either.
    weaponPressedTime = millis() - syncTimeUsed; // Set the time the weapon was pressed.
    weaponPressedFlag = 1;  // Set the flag so we know to send a message
    //Serial.print("Weapon pressed at ");
    //Serial.println(weaponPressedTime);
  }
  portEXIT_CRITICAL_ISR(&mux);
}

//I2C++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
static esp_err_t i2c_slave_init()
{
  i2c_port_t i2c_slave_port = I2C_SLAVE_NUM;
  i2c_config_t conf_slave;
  conf_slave.sda_io_num = I2C_SLAVE_SDA_IO;
  conf_slave.sda_pullup_en = GPIO_PULLUP_ENABLE;
  conf_slave.scl_io_num = I2C_SLAVE_SCL_IO;
  conf_slave.scl_pullup_en = GPIO_PULLUP_ENABLE;
  conf_slave.mode = I2C_MODE_SLAVE;
  conf_slave.slave.addr_10bit_en = 0;
  conf_slave.slave.slave_addr = ESP_SLAVE_ADDR;
  i2c_param_config(i2c_slave_port, &conf_slave);
  return i2c_driver_install(i2c_slave_port, conf_slave.mode,
                            I2C_SLAVE_RX_BUF_LEN,
                            I2C_SLAVE_TX_BUF_LEN, 0);
}

/**
   @brief test function to show buffer
*/
static void disp_buf(uint8_t *buf, int len)
{
  int i;
  for (i = 0; i < len; i++) {
    Serial.printf("%02x ", buf[i]);
    if ((i + 1) % 16 == 0) {
      Serial.printf("\n");
    }
  }
  Serial.printf("\n");
}

uint8_t data[DATA_LENGTH]  ;
uint8_t data_wr[DATA_LENGTH];

uint8_t count;

static void i2c_write_buffer()
{
  int ret;

  if ( i2c_slave_write_buffer(I2C_SLAVE_NUM, data_wr, RW_TEST_LENGTH, 10 / portTICK_RATE_MS) ) {
    Serial.println("buffer written");
    for (int i = 0; i < sizeof(data_wr); i++) {
      Serial.print(data_wr[i]);
    }
    Serial.println();
  }
  else {
    Serial.println("i2c slave tx buffer full"); // should never happen if we only send after each request to read
  }
}


int i2c_read_test()  // returns 0 if nothing has been written to slave
{ int datasize, ret;
  long starttime = micros();
  datasize = i2c_slave_read_buffer(I2C_SLAVE_NUM, data, RW_TEST_LENGTH, 0 / portTICK_RATE_MS); // last term is wait time 0/portTICK_RATE_MS means don't wait
  if (datasize > 0) {
    Serial.printf("---- Slave read: [%d] bytes ----\n", datasize);
    // Send the first byte to the cental computer
    if (data[0] > 0) {
      sendHealing(data[0]);
    }
    disp_buf(data, datasize);
  }
  //else Serial.printf("------ No data to read in %d us \n", micros()-starttime);
  return (datasize);
}

// // I was going to make something more complicated where they actually send the address but I figured it was better to do something quick
//int i2c_handler()  // returns 0 if nothing has been written to slave
//{       int datasize, ret;
//        long starttime = micros();
//        datasize = i2c_slave_read_buffer(I2C_SLAVE_NUM, data, RW_TEST_LENGTH, 0/portTICK_RATE_MS); // last term is wait time 0/portTICK_RATE_MS means don't wait
//        if (datasize > 0) {
//            if (data[0]&&1){ // if it is a read
//              memset(datawr, 0, DATA_LENGTH);  //  clear datawr so their isn't any data left from a previous call
//              data_wr=incomingData>>(8*data[1]); //Shift the data buffer to the right so the byte they want to start with is in the first position
//              i2c_slave_write_buffer(I2C_SLAVE_NUM, data_wr, RW_TEST_LENGTH, 10 / portTICK_RATE_MS);// actually right the buffer
//            }
//            else { // it is a write
//
//            }
//            Serial.printf("---- Slave read: [%d] bytes ----\n", datasize);
//            disp_buf(data, datasize);
//        }
//        //else Serial.printf("------ No data to read in %d us \n", micros()-starttime);
//        return (datasize);
//}

//+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

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
  pinMode(ROBOTID0, INPUT_PULLUP);
  pinMode(ROBOTID1, INPUT_PULLUP);
  pinMode(ROBOTID2, INPUT_PULLUP);
  pinMode(ROBOTID3, INPUT_PULLUP);
  pinMode(ROBOTID4, INPUT_PULLUP);
  pinMode(ROBOTID5, INPUT_PULLUP);

  pinMode(SYNCBEACONPIN, INPUT_PULLUP);

  pinMode(BUTTON, INPUT_PULLUP);
  pinMode(WEAPON, INPUT_PULLUP);

  pinMode(LEDBUILTIN, OUTPUT);

  //Create interups for weapon and button
  attachInterrupt(digitalPinToInterrupt(BUTTON), handleButtonInterrupt, FALLING);
  attachInterrupt(digitalPinToInterrupt(WEAPON), handleWeaponInterrupt, FALLING);

  //+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  for (int i = 0; i < DATA_LENGTH; i++) {
    data_wr[i] = 0;  // put some structured data, just so we can verify it's there
  }


  ESP_ERROR_CHECK(i2c_slave_init());
  //+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


  // setup robot number
  robotNumber = ((!digitalRead(ROBOTID5) << 5) | (!digitalRead(ROBOTID4) << 4) | (!digitalRead(ROBOTID3) << 3) | (!digitalRead(ROBOTID2) << 2) | (!digitalRead(ROBOTID1) << 1) | (!digitalRead(ROBOTID0) << 0));
  Serial.print("Robot Number: ");
  Serial.println(robotNumber);
  Serial.print("MetaTeam: ");
  Serial.println(ceil(robotNumber/4.0));
  Serial.println();

  IPAddress myIPaddress(192, 168, 1, (100 + robotNumber)); // arbitrary address need to send to

  Serial.print("Connecting to ");
  Serial.println(ssid);


  Serial.println(getMacAddress());


  // Connect to the WiFi
  WiFi.begin(ssid, password);
  WiFi.config(myIPaddress, IPAddress(192, 168, 1, 1), IPAddress(255, 255, 255, 0));

  // Wait for connection
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("WiFi connected");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
  // Start listening for traffic
  //serverReceive.begin();
  //serverReceive.setNoDelay(true);
  //udp.begin(WiFi.localIP(),udpPort);
  udpSync.begin(udpSyncPort);
  udpReceive.begin(udpReceivePort);
  

  // Sync Beacon.  This sends a Sync response with number 0 to Central to let it know that we just rebooted and need to sync.
  char syncPacket[] = {robotNumber, 255};
  //cli = serverSend.available();
  bool messageSent = !digitalRead(SYNCBEACONPIN);
  while (!messageSent) {
    delay(100);
    Serial.println("I need to sync!");
    cli.connect(centralIP, TCPSyncPort); //!!!!!!!!!    11/5 Diego
    if (cli) {
      cli.print(syncPacket);
      Serial.println("Sync Response sent");
      messageSent = 1;
      //serverSend.write(syncPacket,sizeof(syncPacket)); //(data bytes to send, number of bytes of the data)
    } 
  }
  wdtInit();  // need to init at the end or it will reset on one missed message

  Serial.println("End of Setup");

}

void loop() {
  //Serial.println("it begins");

  timerWrite(timer, 0); //reset timer (feed watchdog)

  static bool gameStatus = 0;              // game on 1, game off 0
  static bool reset = 0;                   // 1 for reseting, not sure what the intention is here, check with Diego
  static bool autoMode = 0;                // 0 not autonomous, 1 is autonomous

  static bool syncStatus = 0;              // 0 sync still hasn't happend, 1 sync has happend
  static bool syncStatusPrev = syncStatus;              // 0 sync still hasn't happend, 1 sync has happend
  static byte coolDownStatus = 0;          // 0 ready to hit, 1 cooling down

  static byte healthRobot[8];      // health of each robot as a byte
  static byte healthNexus[4];      // health of the two nexi each is 10 bit
  static byte towerStatus[2];      // status of the two towers.  Not sure why this needs 4 bits each.

  static byte redMetaTeam;
  static byte blueMetaTeam;
  
  //static unsigned int incomingDataAddress= incomingData;
  static int packetNumber = 0;  // Used to track if a new packet has come in
  static int packetNumberOld;  // Used to track if a new packet has come in

  // char packetBuffer[2]; //buffer to hold incoming packet

  packetNumberOld = packetNumber;
  //packetNumber = handleTCPserver(incomingDataAddress);
  //Serial.println("374");
  // If something happened send that info

  int metaTeam = ceil(robotNumber/4.0);
  if ((metaTeam==redMetaTeam | (metaTeam==blueMetaTeam ) | redMetaTeam == ACCEPTALLTCP | blueMetaTeam == ACCEPTALLTCP)){
    sendButtonPress();
    //Serial.println("378");
    sendWeaponPress();
  }
//  else{
//    Serial.println("YOUR TEAM IS NOT PLAYING, PLEASE DO NOT CREATE WIFI INTERFERENCE");
//  }

  // -----------------------------------------------------------------
  // Changed to reading from udp
  //Serial.println("384");
  int packetSize = udpReceive.parsePacket();
  if (packetSize) {
    digitalWrite(LEDBUILTIN, !digitalRead(LEDBUILTIN));
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
    Serial.println("Contents:");
    for (int i = 0; i < len; i++) {
      Serial.println(incomingData[i]);
    }
    packetNumber++;
    udpReceive.flush();
    //Serial.println("407");
  }

  // -----------------------------------------------------------------


  //==========================================================================================================
  // Sync with UDP
  //Serial.println("415");
  if ((syncTime == 0) | ~syncStatus) {
    //read udp
    int packetSize = udpSync.parsePacket();
    if (packetSize) {
      //Serial.println("420");
      syncTime = millis(); // if you get a packet the sync get the offset for syncing

      Serial.print("Received packet of size ");
      Serial.println(packetSize);
      Serial.print("From ");
      //IPAddress centralIP = udpSync.remoteIP();
      Serial.print(centralIP);
      Serial.print(", port ");
      Serial.println(udpSync.remotePort());

      // read the packet into packetBufffer
      int len = udpSync.read(packetBuffer, 2);
      if (len > 0) {
        packetBuffer[len] = 0;
      }
      Serial.println("Contents:");
      Serial.println((byte)packetBuffer[0]);
      udpSync.flush();
      byte udpPacketNumber = packetBuffer[0]; // the number of the sync packet sent, specific to how we are organizing things.
      //Serial.println("440");
      // send the TCP response
      char syncPacket[] = {robotNumber, udpPacketNumber};
      //cli = serverSend.available();
      
      if ((metaTeam==redMetaTeam | (metaTeam==blueMetaTeam ) | redMetaTeam == ACCEPTALLTCP | blueMetaTeam == ACCEPTALLTCP)){
        cli.connect(centralIP, TCPSyncPort); //!!!!!!!!!    11/5 Diego
        if (cli) {
          cli.print(syncPacket);
          Serial.println("Sync Response sent");
          //serverSend.write(syncPacket,sizeof(syncPacket)); //(data bytes to send, number of bytes of the data)
          //Serial.println("449");
        }
        cli.stop();
      }
      else{
        Serial.println("YOUR TEAM IS NOT PLAYING, PLEASE DO NOT CREATE WIFI INTERFERENCE");
      }
      Serial.print("Robot Number: ");
      Serial.println(robotNumber);
      //Serial.println();
      Serial.print("syncTime: ");
      Serial.println(syncTime);
      Serial.print("syncTimeUsed: ");
      Serial.println(syncTimeUsed);
      Serial.println();
      //Serial.println("458");
    }
  }

  if (syncStatus > syncStatusPrev){
    syncTimeUsed = syncTime;
  }
  syncStatusPrev = syncStatus;
  //end sync
  //======================================================================================================

  //This is used to determine syncing error.  Debug only.

  // bool ledFlag=0;
  // bool ledVal = 0;
  //  while(syncStatus){
  //     if(!((millis()-syncTime)%100)){
  //      if(!ledFlag){
  //        ledFlag=1;
  //        ledVal = !ledVal;
  //        digitalWrite(LEDBUILTIN,ledVal);
  //
  //      }
  //      }
  //     else{
  //      ledFlag=0;
  //    }
  //  }

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
    Serial.print("Sync Status: ");
    Serial.println(syncStatus);
    Serial.println();
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

    towerStatus[1] = 0x0F & (incomingData[14] >> 0);    // This can be cleaned up because you just need the and for the first one and the shift for the second but I like the consistency.
    towerStatus[2] = 0x0F & (incomingData[14] >> 4);

    redMetaTeam = incomingData[15];
    blueMetaTeam = incomingData[16];
  }

  if (reset) {
    ESP.restart();
  }

  // end parse
  //------------------------------------------------------------------------

  //   //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  //   // I2C Stuff
  //i2c_reset_tx_fifo(I2C_SLAVE_NUM); // clear the fifo so it doesn't fill up if we don't read it.
  //Serial.println("527");
  for (int i = 0; i < 15; i++) {
    data_wr[i] = incomingData[i]; // put the incoming data on the I2C buffer
  }
  //Serial.println("531");
  if (i2c_read_test() > 0) {
    //Serial.println("533");
    //delay(400);
    i2c_write_buffer();
  }
  delay(30);

  //  // +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

}


void sendButtonPress() {
  // send the TCP packet when button pressed
  if (buttonPressedFlag) {
    char packet[] = {WASHIT, buttonPressedTime, buttonPressedTime >> (8 * 1), buttonPressedTime >> (8 * 2), buttonPressedTime >> (8 * 3)};
    buttonPressedFlag = 0;  //clear flag
    Serial.println(buttonPressedTime);
    //cli = serverSend.available();
    Serial.println("trying to send");
    Serial.println(centralIP);
    cli.connect(centralIP, TCPSendPort);
    if (cli) {
      //cli.print(packet);
      cli.write(packet, sizeof(packet));
      Serial.println("I said I was hit");
      //serverSend.write(syncPacket,sizeof(syncPacket)); //(data bytes to send, number of bytes of the data)
    }
    cli.stop();
  }
}

void sendHealing(byte healingFreq) {
  // send the TCP packet when button pressed
  int currentTime = millis();
  static int healingTimeSent = millis();
  if ((currentTime - HEALINGDELAY) >= healingTimeSent) {

    char packet[] = {(HEALING | (healingFreq << 2)), (currentTime), (currentTime >> (8 * 1)), (currentTime >> (8 * 2)), (currentTime >> (8 * 3))};
    Serial.print("packet: ");
    Serial.println(packet[0]);
    Serial.println("trying to send");
    Serial.println(centralIP);
    cli.connect(centralIP, TCPSendPort);
    if (cli) {
      //cli.print(packet);
      cli.write(packet, sizeof(packet));
      Serial.println("give me that sweet sweet health");
      //serverSend.write(syncPacket,sizeof(syncPacket)); //(data bytes to send, number of bytes of the data)
      healingTimeSent = currentTime; // reset the time
    }
    cli.stop();
  }
}

void sendWeaponPress() {
  // send the TCP packet when button pressed
  if (weaponPressedFlag) {
    char packet[] = {MADEHIT, (weaponPressedTime), (weaponPressedTime >> (8 * 1)), (weaponPressedTime >> (8 * 2)), (weaponPressedTime >> (8 * 3))};
    Serial.println(weaponPressedTime);

    weaponPressedFlag = 0;  //clear flag
    //cli = serverSend.available();
    Serial.println("trying to send");
    Serial.println(centralIP);
    cli.connect(centralIP, TCPSendPort);
    if (cli) {
      cli.write(packet, sizeof(packet));
      Serial.println("I said I hit something");
      //          Serial.println(packet[0],BIN);
      //          Serial.println(packet[1],BIN);
      //          Serial.println(packet[2],BIN);
      //          Serial.println(packet[3],BIN);
      //          Serial.println(packet[4],BIN);
      //          Serial.println(sizeof(weaponPressedTime));

      //serverSend.write(syncPacket,sizeof(syncPacket)); //(data bytes to send, number of bytes of the data)
    }
    cli.stop();
  }
}
