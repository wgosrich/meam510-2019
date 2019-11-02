/*
 *  This sketch sends random data over UDP on a ESP32 device
 *
 */
#include <WiFi.h>
#include <WiFiUdp.h>

// WiFi network name and password:
const char * networkName = "Mechatronics";
const char * networkPswd = "YayFunFun";

//IP address to send UDP data to:
// either use the ip address of the server or 
// a network broadcast address
const char * udpAddress = "192.168.0.255";
const int udpPort = 3333;

//Are we currently connected?
boolean connected = false;

//The udp library class
WiFiUDP udp;
WiFiServer serverSend(2222);
WiFiClient cli;

void setup(){
  // Initilize hardware serial:
  Serial.begin(115200);
  
  //Connect to the WiFi network
  connectToWiFi(networkName, networkPswd);
}
char packetBuffer[2];
int robotNumber = 62;
void loop(){
  int packetSize = udp.parsePacket();
  if (packetSize) {
    
    uint32_t syncTime = millis(); // if you get a packet the sync get the offset for syncing
    
    Serial.print("Received packet of size ");
    Serial.println(packetSize);
    Serial.print("From ");
    IPAddress centralIP = udp.remoteIP();
    Serial.print(centralIP);
    Serial.print(", port ");
    Serial.println(udp.remotePort());

    // read the packet into packetBufffer
    int len = udp.read(packetBuffer, 2);
    if (len > 0) {
      packetBuffer[len] = 0;
    }
    Serial.println("Contents:");
    Serial.println((uint8_t) packetBuffer[0]);

    byte udpPacketNumber = packetBuffer[0]; // the number of the sync packet sent, specific to how we are organizing things.

    // send the TCP response
    char syncPacket[] = {udpPacketNumber, robotNumber};
    //cli = serverSend.available();
    cli.connect(centralIP,4444);
    if (cli) {
      cli.print(syncPacket);
      Serial.println("Sync Response sent");
      //serverSend.write(syncPacket,sizeof(syncPacket)); //(data bytes to send, number of bytes of the data)
    }
    cli.stop();
    Serial.print("syncTime: ");
    Serial.println(syncTime);
    Serial.println();
  }
}

void connectToWiFi(const char * ssid, const char * pwd){
  Serial.println("Connecting to WiFi network: " + String(ssid));

  // delete old config
  WiFi.disconnect(true);
  //register event handler
  WiFi.onEvent(WiFiEvent);
  
  //Initiate connection
  WiFi.begin(ssid, pwd);

  Serial.println("Waiting for WIFI connection...");
}

//wifi event handler
void WiFiEvent(WiFiEvent_t event){
    switch(event) {
      case SYSTEM_EVENT_STA_GOT_IP:
          //When connected set 
          Serial.print("WiFi connected! IP address: ");
          Serial.println(WiFi.localIP());  
          //initializes the UDP state
          //This initializes the transfer buffer
          udp.begin(WiFi.localIP(),udpPort);
          connected = true;
          break;
      case SYSTEM_EVENT_STA_DISCONNECTED:
          Serial.println("WiFi lost connection");
          connected = false;
          break;
    }
}
