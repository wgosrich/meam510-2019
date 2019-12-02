#include <WiFi.h>
#include <WiFiUdp.h>

//declare pins
#define LED_BUILTIN 2

//declare variables to hold incoming and outgoing packets
char packetOut[1024];
const int packetSize = 1024;

// WiFi network name and password:
char *networkName = "ESAP2019-2.4";
char *networkPswd = "r0b0tics";

//declare WiFiUDP object
WiFiUDP UDPTestServer;

//set local and target IP addresses and ports
unsigned int UDPLocalPort = 2401;
unsigned int UDPTargetPort = 10000;
IPAddress myIPAddress(192, 168, 1, 101);
IPAddress IPTarget(192,168, 1, 2); 

void setup() {
  Serial.begin(115200);

  //set output & input pins
  pinMode(LED_BUILTIN, OUTPUT); //for builtin LED

  //Connect to the WiFi network with set local IP address & port
  WiFi.begin(networkName, networkPswd);
  WiFi.config(myIPAddress, IPAddress(192, 168, 1, 1), IPAddress(255, 255, 255, 0));
  UDPTestServer.begin(UDPLocalPort);

  while(WiFi.status() != WL_CONNECTED) { //wait to connect to WiFi
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("WiFi connected");
  //use as station
  WiFi.mode(WIFI_STA);
}

void loop() {
  int i;
  for(char i = 0x01; i <= 0xff; i++) {
    packetOut[0] = i;
    packetOut[1] = i;
    packetOut[2] = 0;
    UDPTestServer.beginPacket(IPTarget, UDPTargetPort);
    UDPTestServer.printf("%s", packetOut);
    UDPTestServer.endPacket();
  
    Serial.println("Packet sent");
    delay(1000); //delay to reduce frequency of polling
  }
}
