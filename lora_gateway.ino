//Import all library needed
#include <LoRa.h>
#include <SPI.h>

//Define all the pin used
#define ss 5
#define rst 14
#define dio0 2

//Declare all the variable
String LoRaData;
String loRaMessage;
String senseValue;
String readingID;
String nodeID;


void setup(){
  Serial.begin(115200); //Baudrate
  //Serial.println("LoRa Receiver");
  LoRa.setPins(ss, rst, dio0);    
  while (!LoRa.begin(433E6)){ //Start LoRa communication Interface
      //Serial.println(".");
      delay(500);
    }
  LoRa.setSyncWord(0xA5);
  //Serial.println("LoRa is initialized!");
}

void loop(){
  int packetSize = LoRa.parsePacket(); //Parse the packet
  if (packetSize) 
  { 
    //Serial.println("Received packet");
    while (LoRa.available())              
    {
      LoRaData = LoRa.readString();  //Read the LoRa data
      Serial.println(LoRaData); //Print in the serial
    
      nodeID = LoRaData.substring(0,1);
      int pos1 = LoRaData.indexOf('/');      
      readingID = LoRaData.substring(1, pos1);              
      senseValue = LoRaData.substring(pos1 +1, LoRaData.length());
      Serial.println(String(readingID) + String(senseValue));
    }
    //Serial.print(" with LoRa RSSI= ");
    //Serial.print(LoRa.packetRssi());
  }
}
