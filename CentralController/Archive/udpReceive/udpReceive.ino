#include <WiFi.h>
#include <WiFiUdp.h>
#include <esp32-hal-ledc.h>

#define LED_BUILTIN 2

// WiFi network name and password:
char * networkName = "AslamahFi";
char * networkPswd = "finewhatever";

// Internet port to request from:
int hostPort = 5555;

char packetBuffer[100]; //buffer to hold incoming packet

WiFiUDP Udp; //declare WiFiUDP object

void setup() {
  Serial.begin(115200);
  //set output pins
  pinMode(LED_BUILTIN, OUTPUT);
  
  // Connect to the WiFi network
  connectToWiFi(networkName, networkPswd);

  Udp.begin(hostPort);
}

void loop() {
  // if there's data available, read a packet
  int packetSize = Udp.parsePacket();
  if (packetSize) {
    Serial.print("Received packet of size ");
    Serial.println(packetSize);
    Serial.print("From ");
    IPAddress remoteIp = Udp.remoteIP();
    Serial.print(remoteIp);
    Serial.print(", port ");
    Serial.println(Udp.remotePort());

    // read the packet into packetBufffer
    int len = Udp.read(packetBuffer, 100);
    if (len > 0) {
      packetBuffer[len] = 0;
    }
    Serial.println("Contents:");
    Serial.println(packetBuffer);
  }
  
  //Wait for 1 millisecond to avoid polling too often and overloading router
  delay(1000);
}

void connectToWiFi(char * ssid, char * pwd)
{
  int ledState = 0;

  Serial.println("Connecting to WiFi network: " + String(ssid));

  WiFi.begin(ssid, pwd);

  while (WiFi.status() != WL_CONNECTED) 
  {
    // Blink LED while we're connecting:
    digitalWrite(LED_BUILTIN, ledState);
    ledState = (ledState + 1) % 2; // Flip ledState
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("WiFi connected!");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  digitalWrite(LED_BUILTIN, LOW); // LED off
}

int choose_pwm(int value)
{
  //choose PWM based on input from broadcast
  switch(value)
  {
    case 0: return 0;
    case 1: return 256/4;
    case 2: return 256/2;
    case 3: return 255;
  }
}
