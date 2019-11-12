#include "WiFi.h"
 
const char *ssid = "mechatronics";
const char *password = "meam5102019";
 
void setup() {
 
  Serial.begin(115200);
  WiFi.softAP(ssid, password);
 
  Serial.println();
  Serial.print("IP address: ");
  Serial.println(WiFi.softAPIP());
 
}
 
void loop() {}
