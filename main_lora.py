#Radityo Fajar Pamungkas - Main LoRa program

#Import all library needed
import json
import serial

#get data using serial communication
lora = serial.Serial('COM6', 115200)

while True:
        try:
        #Read and convert data to JSON format
            data = (lora.readline().decode('utf-8').rstrip())
            data = data.replace("'", '"')
            data = data.replace('"{ ', "{")
            data = data.replace('}"', "}")
            jsonData = json.loads(data)
            #print(jsonData)
        
        #Parse data
            Id = jsonData['ID']
            nid = jsonData['nid']
            Dust = jsonData['Dust']
            Temp = jsonData['Temp']
            Hum = jsonData['Hum']
            
            print('ID: ' + str(Id) + ", Dust: " + str(Dust) + ", Temp: " + str(Temp) + ", Hum: " + str(Hum))
            
        except Exception as e:
            print(e)        
