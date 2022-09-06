#Radityo Fajar Pamungkas - LoRa + Adaptive Threshold Isolation Forest

#Import all library needed
import json
import serial
import numpy as np
from sklearn.ensemble import IsolationForest
from joblib import load, dump
import threading
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

lora = serial.Serial('COM6', 115200)

#Thresholding value = can be set as the range 
#healthy temperature & humidity conditions in smart home
threshold_temp_lower = 0.0
threshold_temp_higher = 35.0
threshold_hum_lower = 20.0
threshold_hum_higher = 65.0

#Sliding window setting
batch_size = 5
train_number = 50

#Model parameter
outlier_fraction_param = 0.01 #1% error

#Clustering setting
anomaly_thresTemp_param = 2
anomaly_thresHum_param = 2

#Declare all library and array
nid_library = {} #Temperature
nid_library2 = {} #Humidity

def train(nid, outlier_fraction_temp, outlier_fraction_hum):
    global outlier_fraction_param
    global nid_library, nid_library2

    #Model setting
    estimator = 100
    samples = 1000
    randstate = 42

    #outlier parameter
    if outlier_fraction_temp == 0:
        outlier_fraction_temp = 1e-3
    elif outlier_fraction_temp >= outlier_fraction_param:
        outlier_fraction_temp = outlier_fraction_param
    else:
        outlier_fraction_temp = outlier_fraction_temp

    if outlier_fraction_hum == 0:
        outlier_fraction_hum = 1e-3
    elif outlier_fraction_hum >= outlier_fraction_param:
        outlier_fraction_hum = outlier_fraction_param
    else:
        outlier_fraction_hum = outlier_fraction_hum
    
    #model initialization
    model_temp = IsolationForest(n_estimators=estimator, max_samples=samples, random_state=randstate, contamination=outlier_fraction_temp)
    model_hum = IsolationForest(n_estimators=estimator, max_samples=samples, random_state=randstate, contamination=outlier_fraction_hum)

    #data preprocess
    data_temp = nid_library[nid].reshape(-1,1)
    data_hum = nid_library2[nid].reshape(-1,1)

    #model training
    model_temp.fit(data_temp)
    model_hum.fit(data_hum)

    #filename
    var1 = 'model\model_'
    var_temp = '_temp.joblib'
    var_hum = '_hum.joblib'
    filename_temp_model = var1 + str(nid) + var_temp
    filename_hum_model = var1 + str(nid) + var_hum

    #save/overwrite model
    dump(model_temp, filename_temp_model)
    dump(model_hum, filename_hum_model)
    print('Update the model')

while True:
        try:
            data = (lora.readline().decode('utf-8').rstrip())
            data = data.replace("'", '"')
            data = data.replace('"{', "{")
            data = data.replace('}"', "}")
            jsonData = json.loads(data)
            #print(jsonData)

            Id = jsonData['ID']
            nid = jsonData['nid']
            Dust = jsonData['Dust']
            Temp = jsonData['Temp']
            Hum = jsonData['Hum']

            print('ID: ' + str(Id) + ", Dust: " + str(Dust) + ", Temp: " + str(Temp) + ", Hum: " + str(Hum))

            sensor_temp = np.array([float(Temp)]).T
            sensor_hum = np.array([float(Hum)]).T

            score_nid = 'score_' + str(nid)
            status_nid = 'status_' + str(nid)
            counter = 'counter_' + str(nid)
            anomaly_thresTemp = 'thresholdTemp_' + str(nid)
            anomaly_thresHum = 'thresholdHum_' + str(nid)

            if nid not in nid_library.keys(): #Check whether nid is new or not
                #Temperature
                nid_library[nid] = np.array([[]]) 
                nid_library[score_nid] = np.array([[]])
                nid_library[status_nid] = np.array([[]])
                nid_library[anomaly_thresTemp] = 0.0

                #Humidity
                nid_library2[nid] = np.array([[]])
                nid_library2[score_nid] = np.array([[]])
                nid_library2[status_nid] = np.array([[]])
                nid_library2[anomaly_thresHum] = 0.0

                nid_library[counter] = 1
            
            #input stream data to the window
            nid_library[nid] = np.append(nid_library[nid], sensor_temp) #temperature
            nid_library2[nid] = np.append(nid_library2[nid], sensor_hum) #humidity

            print('counter: ' + str(nid_library[counter]))

            if nid_library[counter] == 1:
                #Mode 1: using initial model
                try: #if specified model is already built
                    #filename
                    var1 = 'model\model_'
                    var_temp = '_temp.joblib'
                    var_hum = '_hum.joblib'

                    filename_temp_model = var1 + str(nid) + var_temp
                    filename_hum_model = var1 + str(nid) + var_hum
                    model_temp = load(filename_temp_model)
                    model_hum = load(filename_hum_model)
                    
                except: #if there is no specified model
                    #filename
                    print('no specified model')
                    filename_temp_model = 'model\model_temp_initial.joblib'
                    filename_hum_model = 'model\model_hum_initial.joblib'
                    model_temp = load(filename_temp_model)
                    model_hum = load(filename_hum_model)
                
                finally:
                    #load model
                    print(filename_temp_model)
                    print(filename_hum_model)
                    

                    nid_library[counter] += 1
            
            elif nid_library[counter] <= batch_size:
                #Mode 2: Keep using initial model until the data stored in array
                nid_library[counter] += 1

            elif nid_library[counter] == (batch_size + 1):
                #Mode 3: re-training the model

                #Calculate the outlier fraction
                outlier_temp = Counter(nid_library[status_nid])
                outlier_hum = Counter(nid_library2[status_nid])
                outlier_fraction_temp = (len(nid_library[nid]) - outlier_temp['normal']) / len(nid_library[status_nid])
                outlier_fraction_hum = (len(nid_library[nid]) - outlier_hum['normal']) / len(nid_library2[status_nid])

                print('outlier fraction temp: ' + str(outlier_fraction_temp))
                print('outlier freaction hum: ' + str(outlier_fraction_hum))

                #multithreading
                thread = threading.Thread(target=train, args=(nid, outlier_fraction_temp, outlier_fraction_hum))
                if thread.is_alive():
                    print('thread still running')
                else:
                    print('thread is starting')
                    thread.start()
                nid_library[counter] += 1
                thread.join()

            elif nid_library[counter] == (batch_size+2):
                #Mode 4: Load retrained model

                #filename
                var1 = 'model\model_'
                var_temp = '_temp.joblib'
                var_hum = '_hum.joblib'
                filename_temp_model = var1 + str(nid) + var_temp
                filename_hum_model = var1 + str(nid) + var_hum

                #load model
                model_temp = load(filename_temp_model)
                model_hum = load(filename_hum_model)
                print('Retrained model loaded')

                #calculate the anomaly score threshold for temperature
                anomaly_score_temp_mean = nid_library[score_nid].mean()
                anomaly_score_temp_std = nid_library[score_nid].std()
                anomaly_score_temp_cal = anomaly_score_temp_mean - (anomaly_score_temp_std*anomaly_thresTemp_param)
                print('temp score mean: ' + str(anomaly_score_temp_mean))
                print('temp score std: ' + str(anomaly_score_temp_std))
                print('temp score cal: ' + str(anomaly_score_temp_cal))

                if anomaly_score_temp_cal <= -0.15:
                    nid_library[anomaly_thresTemp] = -0.15
                elif anomaly_score_temp_cal >= 0.0:
                    nid_library[anomaly_thresTemp] = 0.0
                else:
                    nid_library[anomaly_thresTemp] = anomaly_score_temp_cal

                #calculate the anomaly score threshold for humidity
                anomaly_score_hum_mean = nid_library2[score_nid].mean()
                anomaly_score_hum_std = nid_library2[score_nid].std()
                anomaly_score_hum_cal = anomaly_score_hum_mean - (anomaly_score_hum_std*anomaly_thresHum_param)
                print('hum score mean: ' + str(anomaly_score_hum_mean))
                print('hum score std: ' + str(anomaly_score_hum_std))
                print('hum score cal: ' + str(anomaly_score_hum_cal))

                if anomaly_score_hum_cal <= -0.15:
                    nid_library2[anomaly_thresHum] = -0.15
                elif anomaly_score_hum_cal >= 0.0:
                    nid_library2[anomaly_thresHum] = 0.0
                else:
                    nid_library2[anomaly_thresHum] = anomaly_score_hum_cal

                nid_library[counter] += 1

            elif nid_library[counter] <= (batch_size + batch_size):
                #Mode 5: Sliding window method
                nid_library[counter] += 1

            else:
                #optimize the array size of sliding window (for temperature)
                nid_library[nid] = nid_library[nid][-(train_number+2*batch_size):]
                nid_library[score_nid] = nid_library[score_nid][-(train_number+2*batch_size):]
                nid_library[status_nid] = nid_library[status_nid][-(train_number+2*batch_size):]

                #optimize the array size of sliding window (for humidity)
                nid_library2[nid] = nid_library2[nid][-(train_number+2*batch_size):]
                nid_library2[score_nid] = nid_library2[score_nid][-(train_number+2*batch_size):]
                nid_library2[status_nid] = nid_library2[status_nid][-(train_number+2*batch_size):]

                nid_library[counter] = (batch_size + 1)

            #preprocess the data for anomaly detection
            sensor_temp_reshape = sensor_temp.reshape(-1,1)
            sensor_hum_reshape = sensor_hum.reshape(-1,1)

            #anomaly detection / Isolation Forest Prediction
            anomaly_score_temp = model_temp.decision_function(sensor_temp_reshape)
            anomaly_score_hum = model_hum.decision_function(sensor_hum_reshape)

            #print the value in the terminal
            print('temp value: ' + str(Temp))
            print('temp score: ' + str(float(anomaly_score_temp)))
            print('temp threshold: ' + str(float(nid_library[anomaly_thresTemp])))
            print('hum value: ' + str(Hum))
            print('hum score: ' + str(float(anomaly_score_hum)))
            print('hum threshold: ' + str(float(nid_library2[anomaly_thresHum])))

            #Clustering between normal and abnormal
            
            #Temperature sensor
            if float(Temp) > threshold_temp_lower:
                if float(Temp) < threshold_temp_higher:
                    if anomaly_score_temp >= nid_library[anomaly_thresTemp]:
                        #Normal condition
                        sensor_temp_status = 'normal'
                    else:
                        #Abnormal condition: detected by isolation forest
                        sensor_temp_status = 'abnormal'
                else:
                    #Abnormal condition: detected by thresholdAD (sensor value too high)
                    sensor_temp_status = 'Abnormal/too high'
            else:
                #Abnormal condition: detected by thresholdAD (sensor value too low)
                sensor_temp_status = 'Abnormal/too low'
            print('sensor temp status: ' + str(sensor_temp_status))
            #Humidity Sensor
            if float(Hum) > threshold_hum_lower:
                if float(Hum) < threshold_hum_higher:
                    if anomaly_score_hum >= nid_library2[anomaly_thresHum]:
                        #normal condition
                        sensor_hum_status = 'normal'
                    else:
                        #abnromal condition: detected by isolation forest
                        sensor_hum_status = 'abnormal'
                else:
                    #abnormal condition: detected by thresholdAD (sensor value too high)
                    sensor_hum_status = 'abnormal/too high'
            else:
                #abnormal condition: detected by thresholdAD (sensor value too low)
                sensor_hum_status = 'abnormal/too low'
            print('sensor hum status: ' + str(sensor_hum_status))
            #append value of anomaly score and sensor status
            nid_library[score_nid] = np.append(nid_library[score_nid], float(anomaly_score_temp))
            nid_library[status_nid] = np.append(nid_library[status_nid], sensor_temp_status)

            nid_library2[score_nid] = np.append(nid_library2[score_nid], float(anomaly_score_hum))
            nid_library2[status_nid] = np.append(nid_library2[status_nid], sensor_hum_status)

            print('window_size: ' + str(len(nid_library[nid])))

        except Exception as e:
            print(e)
        
