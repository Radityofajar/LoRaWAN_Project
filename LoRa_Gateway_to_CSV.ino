#include <LoRa.h>
#include <SPI.h>
#include <WiFi.h>

#define ss 5
#define rst 14
#define dio0 2
String LoRaData;
String loRaMessage;
String senseValue;
String readingID;
String nodeID;
const char* ssid     = "Wifi_name";
const char* password = "wifi_pass";
const char* host = "IP_address";


void setup()
{
  
    Serial.begin(115200);
    Serial.println();
    Serial.println();
    Serial.print("Connecting to ");
    Serial.println(ssid);

//    IPAddress ip_static(192, 168, 1, 20);    
//    IPAddress ip_gateway(192,168,1,1); 
//    IPAddress ip_subnet(255,255,255,0); 
//    
//    WiFi.config(ip_static, ip_gateway, ip_subnet); 
    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }

    Serial.println("");
    Serial.println("WiFi connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
    Serial.println("LoRa Receiver");
    LoRa.setPins(ss, rst, dio0);    
    while (!LoRa.begin(433E6))     
    {
      Serial.println(".");
      delay(500);
    }
    LoRa.setSyncWord(0xA5);
    Serial.println("LoRa is initialized!");
}

void loop()
{
  int packetSize = LoRa.parsePacket();    
  if (packetSize) 
  { 
    Serial.println("Received packet");
    while (LoRa.available())              
    {
      LoRaData = LoRa.readString();  
      Serial.print(LoRaData); 
    
      nodeID = LoRaData.substring(0,1);
      int pos1 = LoRaData.indexOf('/');      
      readingID = LoRaData.substring(1, pos1);              
      senseValue = LoRaData.substring(pos1 +1, LoRaData.length()); 
    }
    Serial.print(" with LoRa RSSI= ");
    Serial.print(LoRa.packetRssi());
    Serial.println();
    Serial.print("connecting to ");
    Serial.println(host);

    WiFiClient client;
    const int httpPort = 80;
    if (!client.connect(host, httpPort)) {
        Serial.println("connection failed");
        return;
    }
  
    if (nodeID == "c")
    {
        client.print(String("GET http://IP_address/lora_temp/loratocsv.php?") + 
                          ("&node03=") + readingID + ("&dust=") + senseValue +
                          " HTTP/1.1\r\n" +
                 "Host: " + host + "\r\n" +
                 "Connection: close\r\n\r\n");
    }
    unsigned long timeout = millis();
    while (client.available() == 0) {
        if (millis() - timeout > 1000) {
            Serial.println(">>> Client Timeout !");
            client.stop();
            return;
        }
    }

    while(client.available()) {
        String line = client.readStringUntil('\r');
        Serial.print(line);
        
    }

    Serial.println();
    Serial.println("closing connection");
  }

}
