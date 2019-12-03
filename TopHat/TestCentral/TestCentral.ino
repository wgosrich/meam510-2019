/*
 * Code for TestCentral
 * 
 * TestCentral is an ESP in AP mode that constantly broadcasts the same information over and over again
 */

#include <WiFi.h>
#include <WiFiUDP.h>

// WiFi name
const char* ssid = "TestCentral";
const char* pass = "r0b0tics";

// IP Addresses
IPAddress IPlocal(192,168,1,2);
IPAddress IPbroad(192,168,1,255);

// variables for UDP
WiFiUDP udp;
const int packetSize = 128;
byte sendBuffer[packetSize];
unsigned int UDPlocalPort = 2100;

// Pins
#define GAME_STATE  19
#define AUTO_MODE   18

const int gameStateLED = 22;
const int autoModeLED = 23;

void setup() 
{
    Serial.begin(115200);
    Serial.println("Start of Setup");

    // setup pins for DIP to control game state and auto mode
    pinMode(GAME_STATE, INPUT_PULLUP);
    pinMode(AUTO_MODE, INPUT_PULLUP);

    pinMode(gameStateLED, OUTPUT);
    pinMode(autoModeLED, OUTPUT);

    pinMode(LED_BUILTIN, OUTPUT);

    // setup WiFi Network
    WiFi.mode(WIFI_AP);
    WiFi.softAP(ssid, pass);
    delay(100);

    Serial.print("Set softAPConfig "); Serial.println(ssid);    // debug statement
    
    IPAddress gateway(192,168,1,1);                 // initializes gateway IP
    IPAddress subnet(255,255,255,0);                // initializes subnet mask
    WiFi.softAPConfig(IPlocal, gateway, subnet);    // sets the IP addr of ESP to IPlocal

    udp.begin(UDPlocalPort);

    IPAddress myIP = WiFi.softAPIP();
    Serial.print("AP IP address: "); Serial.println(myIP);
}

void loop() 
{
    // read DIP switch
    int gameState = !digitalRead(GAME_STATE);
    int autoMode = !digitalRead(AUTO_MODE);
    
    digitalWrite(gameStateLED, gameState);
    digitalWrite(autoModeLED, autoMode);

    Serial.print("game: ");
    Serial.println(gameState);
    Serial.print("auto: ");
    Serial.println(autoMode);

    // create the message
    sendBuffer[0]  = (1 << 3) | (autoMode << 2) | (gameState << 0); // 1 to make sure it's non-zero
    Serial.print("buffer0: ");
    Serial.println(sendBuffer[0]);
    sendBuffer[1]  = 0xFF;
    sendBuffer[2]  = 0xFF;
    sendBuffer[3]  = 0xFF;
    sendBuffer[4]  = 0xFF;
    sendBuffer[5]  = 0xFF;
    sendBuffer[6]  = 0xFF;
    sendBuffer[7]  = 0xFF;
    sendBuffer[8]  = 0xFF;
    // blue robot health
    sendBuffer[9]  = 5;
    sendBuffer[10] = 10;
    sendBuffer[11] = 15;
    sendBuffer[12] = 20;
    // end blue robot health
    sendBuffer[13] = 0xFF;
    sendBuffer[14] = 0xFF;
    sendBuffer[15] = 0xFF;
    sendBuffer[16] = 0xFF;
    sendBuffer[17] = 0xFF;
    sendBuffer[18] = 0xFF;
    sendBuffer[19] = 0xFF;
    sendBuffer[20] = 0xFF;
    sendBuffer[21] = 0xFF;
    sendBuffer[22] = 0xFF;
    sendBuffer[23] = 0xFF;
    sendBuffer[24] = 0xFF;
    sendBuffer[25] = 0x00;

    // broadcast message over UDP
    digitalWrite(LED_BUILTIN, HIGH);
    udp.beginPacket(IPbroad, 5555);
    udp.printf("%s", sendBuffer);
    udp.endPacket();

    delay(50);
    digitalWrite(LED_BUILTIN, LOW);
}
