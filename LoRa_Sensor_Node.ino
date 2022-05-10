#include <SPI.h>
#include <LoRa.h>

#define ss 5
#define rst 14
#define dio0 2
#define BAND 433E6 

int readingID = 0;
int counter = 0;
String LoRaMessage = "";
 
int pin = 4;
unsigned long duration;
unsigned long starttime;
unsigned long sampletime_ms = 3000;
unsigned long lowpulseoccupancy = 0;
float ratio = 0;
float concentration = 0;

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
 
void getReadings(){
  duration = pulseIn(pin, LOW);
  lowpulseoccupancy = lowpulseoccupancy+duration;
  if ((millis()-starttime) > sampletime_ms)
  {
    ratio = lowpulseoccupancy/(sampletime_ms*10.0); 
    concentration = 1.1*pow(ratio,3)-3.8*pow(ratio,2)+520*ratio+0.62; 
    Serial.print("concentration = ");
    Serial.print(concentration);
    Serial.println(" pcs/0.01cf  -  ");
    lowpulseoccupancy = 0;
    starttime = millis();
  }
}
 
void sendReadings() {
  LoRaMessage = "c" + String(readingID) + "/" + String(concentration) ;
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
}

void loop() {
  delay(5000);
  getReadings();
  sendReadings();
  delay(5000);
}
