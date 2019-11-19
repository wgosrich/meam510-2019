/************************************************************
    HAT code
    This code recieves game and health information from a central control center over WiFi.
    It also acts as an I2C slave to present that information.

    IP Address of top hat is (100 + teamNumber)

    IO
        WHISKER 23

        SCL   33
        SDA   25

        DIP 1 4
        DIP 2 16
        DIP 3 17
        DIP 4 22
        DIP 5 18
        DIP 6 19
        DIP 7 21

************************************************************/

// ========================= includes =============================
#include <WiFi.h>
#include <WiFiUdp.h>
#include "esp_system.h"
#include "robotNumToMetaTeam.h"


// =================================================================
// ========================= I2C start =============================
// =================================================================
#include <stdio.h>
#include "esp_log.h"
#include "driver/i2c.h"
#include "sdkconfig.h"

#define _I2C_NUMBER(num) I2C_NUM_##num   
#define I2C_NUMBER(num) _I2C_NUMBER(num)
#define DATA_LENGTH 128                         // data buffer length of test buffer
#define RW_TEST_LENGTH 128                      // data length for r/w test, [0,DATA_LENGTH]
#define DELAY_TIME_BETWEEN_ITEMS_MS 1000        // delay time between different test items

#define I2C_SLAVE_SCL_IO (gpio_num_t)33         // gpio number for i2c slave clock
#define I2C_SLAVE_SDA_IO (gpio_num_t)25         // gpio number for i2c slave data
#define I2C_SLAVE_NUM I2C_NUMBER(0)             // i2c port number for slave dev
#define I2C_SLAVE_TX_BUF_LEN (2*DATA_LENGTH)    // i2c slave tx buffer size
#define I2C_SLAVE_RX_BUF_LEN (2*DATA_LENGTH)    // i2c slave rx buffer size

#define ESP_SLAVE_ADDR 0x28                     // ESP32 slave address, can set any 7bit value

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
    for (i = 0; i < len; i++) 
    {
        Serial.printf("%02x ", buf[i]);
        if ((i + 1) % 16 == 0) 
        {
            Serial.printf("\n");
        }
    }
    Serial.printf("\n");
}

uint8_t data[DATA_LENGTH];
uint8_t data_wr[DATA_LENGTH];

uint8_t count;

static void i2c_write_buffer()
{
    int ret;

    if (i2c_slave_write_buffer(I2C_SLAVE_NUM, data_wr, RW_TEST_LENGTH, 10 / portTICK_RATE_MS)) 
    {
        Serial.println("buffer written");
        for (int i = 0; i < sizeof(data_wr); i++) 
        {
            Serial.print(data_wr[i]);
        }
        Serial.println();
    }
    else 
    {
        Serial.println("i2c slave tx buffer full"); // should never happen if we only send after each request to read
    }
}


int i2c_read_test()  // returns 0 if nothing has been written to slave
{ 
    int datasize, ret;
    long starttime = micros();
    datasize = i2c_slave_read_buffer(I2C_SLAVE_NUM, data, RW_TEST_LENGTH, 0 / portTICK_RATE_MS); // last term is wait time 0/portTICK_RATE_MS means don't wait
    if (datasize > 0) 
    {
        Serial.printf("---- Slave read: [%d] bytes ----\n", datasize);
        disp_buf(data, datasize);
    }
    //else Serial.printf("------ No data to read in %d us \n", micros()-starttime);
    return (datasize);
}

// =================================================================
// ========================== I2C end ==============================
// =================================================================


// ========================= WiFi start =============================

// credentials
const char* ssid     = "TestCentral";
const char* password = "r0b0tics";

// IP Addresses
IPAddress centralIP(192,168,1,2); // IP address for central

// TCP
WiFiClient cli; // setup a wifi client to open communication with the main server
const int tcpSendPort = 4444;

// UDP
WiFiUDP udp;
const int udpReceivePort = 5555;
const int udpCentralTargetPort = 10000;

#define INCOMING_MESSAGE_SIZE 128

byte incomingData[INCOMING_MESSAGE_SIZE];
byte outgoingData[INCOMING_MESSAGE_SIZE];

// ========================== WiFi end ==============================

// ==================== Game variables start ========================

// Pins
#define ROBOTID0 4
#define ROBOTID1 16
#define ROBOTID2 17
#define ROBOTID3 22
#define ROBOTID4 18
#define ROBOTID5 19

#define WHISKER 23

//#define SCL 33    // unnecessary, SCL variable isn't used
//#define SDA 25    // unnecessary, SDA variable isn't used

// delay this many ms after the whisker is hit before it can change again
#define WHISKER_HIT_CD  300

// max respawn wait time (in seconds)
#define RESPAWN_TIME    15

byte teamNumber;                            // team number (Canvas)
byte metaTeamNumber;                        // meta team number
byte robotNumber;                           // robot number (within a meta team: 1-4)
byte maxHealth = -1;                        // track the max health (starting health) of this robot
byte currHealth = maxHealth;                // track the current health of this robot
bool isDead = 0;                            // track if the robot is dead (1 for yes, 0 for no)
volatile unsigned long timeOfDeath = 0;     // track the time that the robot died
byte respawnTimer = RESPAWN_TIME;           // respawn timer

volatile bool whiskerHitFlag = 0;
volatile unsigned long whiskerHitTime = 0;

// ===================== Game variables end =========================

portMUX_TYPE mux = portMUX_INITIALIZER_UNLOCKED;    // needed for interrupts

// Interrupt handlers for whisker switch
void IRAM_ATTR handleWhiskerInterrupt()
{
    portENTER_CRITICAL_ISR(&mux);
    if ((millis() - whiskerHitTime) > WHISKER_HIT_CD)
    {
        // if it has been more than the delay, whisker was hit again
        whiskerHitTime = millis();  // set the time the whisker was hit
        whiskerHitFlag = 1;         // set the flag
        
        if (currHealth != 0)
        {
            currHealth -= 1;            // subtract 1 from current health of robot
            Serial.println("I've been hit :(");
            Serial.print("I now have health: ");
            Serial.println(currHealth);
            if (currHealth == 0)
            {
                // robot has no health and is dead
                isDead = 1;
                timeOfDeath = millis();
                respawnTimer = RESPAWN_TIME;
            }
        }
    }
    portEXIT_CRITICAL_ISR(&mux);
}

// =====================================================================
// ============================= SETUP =================================
// =====================================================================
void setup() 
{
    Serial.begin(115200);
    Serial.println("Start of Setup");
    Serial.println("TopHatCode Version: v1");

    // setup pins
    pinMode(ROBOTID0, INPUT_PULLUP);
    pinMode(ROBOTID1, INPUT_PULLUP);
    pinMode(ROBOTID2, INPUT_PULLUP);
    pinMode(ROBOTID3, INPUT_PULLUP);
    pinMode(ROBOTID4, INPUT_PULLUP);
    pinMode(ROBOTID5, INPUT_PULLUP);

    pinMode(WHISKER, INPUT_PULLUP);

    pinMode(LED_BUILTIN, OUTPUT);

    // create interrupt for whisker
    attachInterrupt(digitalPinToInterrupt(WHISKER), handleWhiskerInterrupt, FALLING);

    // ========================= I2C start =============================
    for (int i = 0; i < DATA_LENGTH; i++) 
    {
        data_wr[i] = 0;  // put some structured data, just so we can verify it's there
    }

    ESP_ERROR_CHECK(i2c_slave_init());
    // ========================== I2C end ==============================

    // setup team number and meta team number
    teamNumber = ((!digitalRead(ROBOTID5) << 5) | (!digitalRead(ROBOTID4) << 4) | (!digitalRead(ROBOTID3) << 3) | (!digitalRead(ROBOTID2) << 2) | (!digitalRead(ROBOTID1) << 1) | (!digitalRead(ROBOTID0) << 0));
    int* team2meta = initTeamNum2MetaNumLUT();
    int* team2bot = initTeamNum2BotNumLUT();
    metaTeamNumber = team2meta[teamNumber];
    robotNumber = team2bot[teamNumber];
    Serial.print("TeamNum: ");
    Serial.print(teamNumber);
    Serial.print("\tMetaTeam: ");
    Serial.print(metaTeamNumber);
    Serial.print("\tRobotNumber: ");
    Serial.println(robotNumber);

    // ========================= WiFi start =============================
    IPAddress myIPaddress(192,168,1,(100+teamNumber));

    Serial.print("Connecting to " ); Serial.println(ssid);

    // connect to wifi
    WiFi.begin(ssid, password);
    WiFi.config(myIPaddress, IPAddress(192,168,1,1), IPAddress(255,255,255,0));

    // wait for connection
    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        Serial.print(".");
    }

    Serial.println("WiFi connected");
    Serial.print("My IP: "); Serial.println(WiFi.localIP());

    // start listening for traffic
    udp.begin(udpReceivePort);
    // ========================== WiFi end ==============================

    Serial.println("End of Setup");
}
// =====================================================================
// ========================== END OF SETUP =============================
// =====================================================================


// =====================================================================
// ============================== LOOP =================================
// =====================================================================
void loop()
{
//    Serial.println("Start loop");

    // 1 byte for game info
    static bool gameStatus = 0;             // game on: 1, game off: 0
    static bool resetStatus = 0;            // 1 for resetting
    static bool autoMode = 0;               // not autonomous mode: 0, is auto mode: 1

    static byte nexusHealth[4];             // health of the two nexi each is 10bit
    static byte redRobotHealth[4];          // health of each robot on the red team as a byte
    static byte blueRobotHealth[4];         // health of each robot on the blue team as a byte
    static byte redRobotPos[4];             // (x,y) position of each red robot
    static byte blueRobotPos[4];            // (x,y) position of each blue robot
    static byte towerStatus;                // status of the 2 towers
    static byte redMetaTeam;                // number of meta team on red side
    static byte blueMetaTeam;               // number of meta team on blue side

    static int packetNumber = 0;            // used to track if a new packet has come in
    static int packetNumberOld;             // used to track if a new packet has come in

    // ===================== UDP receive start =========================
//    Serial.println("Start of UDP");
    int packetSize = udp.parsePacket();

    if (packetSize)
    {
//        digitalWrite(LED_BUILTIN, HIGH);
        Serial.print("Received packet of size: "); Serial.println(packetSize);
        
        // read the data into incomingData buffer
        int len = udp.read(incomingData, INCOMING_MESSAGE_SIZE*2);
        if (len > 0)
        {
            incomingData[len] = 0;
        }
        // print out the contents
        Serial.println("Contents:");
        for (int i = 0; i < len; i++)
        {
            Serial.println(incomingData[i]);
        }
        packetNumber++;
        udp.flush();
//        digitalWrite(LED_BUILTIN, LOW);
    }
//    Serial.println("End of UDP");
    // ====================== UDP receive end ==========================

    // ===================== Parse Data start ==========================
    if ((packetNumber - packetNumberOld))
    {
        // new packet arrived

        // game info
        gameStatus  = 1 & (incomingData[0] >> 0);
        resetStatus = 1 & (incomingData[0] >> 1);
        autoMode    = 1 & (incomingData[0] >> 2);

        // nexus health (4 bytes)
        nexusHealth[0] = incomingData[1];
        nexusHealth[1] = incomingData[2];
        nexusHealth[2] = incomingData[3];
        nexusHealth[3] = incomingData[4];

        // red team robot health (4 bytes)
        redRobotHealth[0] = incomingData[5];
        redRobotHealth[1] = incomingData[6];
        redRobotHealth[2] = incomingData[7];
        redRobotHealth[3] = incomingData[8];

        // blue team robot health (4 bytes)
        blueRobotHealth[0] = incomingData[9];
        blueRobotHealth[1] = incomingData[10];
        blueRobotHealth[2] = incomingData[11];
        blueRobotHealth[3] = incomingData[12];
   
        // red team robot positions (4 bytes)
        redRobotPos[0] = incomingData[13];
        redRobotPos[1] = incomingData[14];
        redRobotPos[2] = incomingData[15];
        redRobotPos[3] = incomingData[16];

        // blue team robot positions (4 bytes)
        blueRobotPos[0] = incomingData[17];
        blueRobotPos[1] = incomingData[18];
        blueRobotPos[2] = incomingData[19];
        blueRobotPos[3] = incomingData[20];

        // tower status (1 byte)
        towerStatus = incomingData[21];

        // meta team (2 bytes)
        redMetaTeam  = incomingData[22];
        blueMetaTeam = incomingData[23];

        // set max health of robot (if necessary)
        if (maxHealth == 255)
        {
//            if (metaTeamNumber == redMetaTeam)
//            {
//                maxHealth = redRobotHealth[robotNumber-1];  // -1 because arrays are 0-indexed
//                currHealth = maxHealth;
//            }
//            else if (metaTeamNumber == blueMetaTeam)
//            {
//                maxHealth = blueRobotHealth[robotNumber-1]; // -1 because arrays are 0-indexed
//                currHealth = maxHealth;
//            }

            // just for allowing the students to test, remove later on
            maxHealth = blueRobotHealth[robotNumber-1];
            currHealth = maxHealth;
        }       
    }
    Serial.print("currHealth: ");
    Serial.println(currHealth);
    // ====================== Parse Data end ===========================


    // ========================= I2C start =============================
    // send information to robot over I2C
    // put data into the I2C buffer
    data_wr[0] = incomingData[0];
    data_wr[1] = currHealth;
    data_wr[2] = respawnTimer;
    
    if (i2c_read_test() > 0)
    {
        i2c_write_buffer();
    }
    delay(30);
    // ========================== I2C end ==============================

    // ====================== UDP send start ===========================
//    // send information to central over UDP
//    // put data into the UDP buffer
//    digitalWrite(LED_BUILTIN, HIGH);
//    outgoingData[0] = (currHealth << 1) | (isDead);
//    outgoingData[1] = 0xFF;     // robot location, but this is not implemented for now
//    outgoingData[2] = 0;        // null termination
//
//    udp.beginPacket(centralIP, udpCentralTargetPort);
//    udp.printf("%s", outgoingData);
//    udp.endPacket();
//    
//    delay(30);
//    
//    digitalWrite(LED_BUILTIN, LOW);
    // ======================= UDP send end ============================

    // ====================== respawn start ============================
    // decrement respawnTimer every second
    if (isDead)
    {
        unsigned long timeSinceDeath = millis() - timeOfDeath;
        respawnTimer = RESPAWN_TIME - floor(timeSinceDeath / 1000);
        respawnTimer = max(0, int(respawnTimer));    // respawnTimer cannot be below 0
        if (respawnTimer == 0)
        {
            // robot should come back alive
            isDead = 0;
            currHealth = maxHealth;
        }
    }
    
    // ======================= respawn end =============================

//    Serial.println("End of loop");
}
// =====================================================================
// ========================== END OF LOOP ==============================
// =====================================================================
