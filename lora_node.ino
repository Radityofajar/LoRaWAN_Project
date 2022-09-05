//Radityo Fajar Pamungkas
//ESP32s with Dust sensor and DHT sensor

//Import all library needed
#include <SPI.h>
#include <LoRa.h>
#include "DHT.h"

//Define all pin used
#define ss 5
#define rst 14
#define dio0 2
#define BAND 433E6 
#define DHTTYPE DHT22
#define DHTPIN 22
int pin = 4;

DHT dht(DHTPIN,DHTTYPE);

int readingID = 0;
int counter = 0;
String LoRaMessage = "";

//Declare all variable needed
unsigned long duration;
unsigned long starttime;
unsigned long sampletime_ms = 3000;
unsigned long lowpulseoccupancy = 0;
float ratio = 0;
float concentration = 0;
float temp = 0;
float hum = 0;

//Starting LoRa communication Interface
void startLoRA()
{
  Serial.begin(115200); 
  while (!Serial);
  Serial.println("LoRa Sender");
  LoRa.setPins(ss, rst, dio0);
  while (!LoRa.begin(BAND))
  {
    Serial.println(".");
    delay(500);
  }
  LoRa.setSyncWord(0xA5);
  Serial.println("LoRa Initializing OK!");
}

//Reading all sensor value (Dust, Temperature, and Humidity)
void getReadings(){
  duration = pulseIn(pin, LOW);
  lowpulseoccupancy = lowpulseoccupancy+duration;
  if ((millis()-starttime) > sampletime_ms)
  {
    ratio = lowpulseoccupancy/(sampletime_ms*10.0); 
    concentration = 1.1*pow(ratio,3)-3.8*pow(ratio,2)+520*ratio+0.62; 
    Serial.print("concentration = ");
    Serial.print(concentration);
    Serial.print(" pcs/0.01cf  -  ");
    temp = dht.readTemperature();
    hum = dht.readHumidity();
    Serial.print("temperature = ");
    Serial.print(temp);
    Serial.print(" - humidity = ");
    Serial.println(hum);
    lowpulseoccupancy = 0;
    starttime = millis();
  }
  
}

//Send the data to the LoRa gateway
void sendReadings() {
  LoRaMessage = "'{ 'ID':" + String(readingID) + ", 'Dust':" + String(concentration)+ ", 'Temp':" + String(temp) + ", 'Hum':" + String(hum) + "}'" ;
  LoRa.beginPacket();
  LoRa.print(LoRaMessage);
  LoRa.endPacket();
  Serial.print("Sending packet: ");
  Serial.println(readingID);
  readingID++;
  Serial.println(LoRaMessage);
}

void setup() {
  Serial.begin(115200);
  pinMode(4,INPUT);
  starttime = millis();
  startLoRA();
  dht.begin();
}

void loop() {
  delay(1000);
  getReadings();
  sendReadings();
  delay(1000);
}
