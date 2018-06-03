import json
import paho.mqtt.client as mqtt
import sha2
import time
import os
import glob
import RPi.GPIO as GPIO
GPIO.setwarnings(False)

pin_to_circuit = 11


# Set Pembacaan Board Raspberri pi sebagai Board Mode
GPIO.setmode(GPIO.BOARD)

# Inisialisasi Sensor Ultrasonic
GPIO_TRIGGER = 8
GPIO_ECHO = 10

GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

#Sensor Suhu
suhu = 0;

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

# Fungsi Sensor LDR
def rc_time (pin_to_circuit):
    count = 0
  
    GPIO.setup(pin_to_circuit, GPIO.OUT)
    GPIO.output(pin_to_circuit, GPIO.LOW)
    time.sleep(0.1)

    GPIO.setup(pin_to_circuit, GPIO.IN)
  
    while (GPIO.input(pin_to_circuit) == GPIO.LOW):
        count += 1

    return count

# Fungsi Sensor Ultrasinic
def distance():
    GPIO.output(GPIO_TRIGGER, True)
 
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
 
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    TimeElapsed = StopTime - StartTime
    distance = (TimeElapsed * 34300) / 2
 
    return distance

# Fungsi Sensor Suhu Data Mentah/ Nilai Voltase
def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

 # Fungsi Sensor Suhu/Pengolahan Untuk Jadi Celcius
def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c


# Inisiasi object mqtt
mqttc = mqtt.Client("pub1", clean_session=True)

# Buat koneksi ke broker
mqttc.connect( "192.168.201.100", 1883 )


while True:
	suhu = read_temp()
	dist = "%.3f" % distance()
	kekeruhan = rc_time(pin_to_circuit)
	
	sensor_ketinggian = str(dist)
	sensor_suhu = str(suhu)
	sensor_kekeruhan = str(kekeruhan)
	
	#string sensor 1 + sensor 2 + sensor 3
	group_data_sensor = sensor_kekeruhan + sensor_suhu + sensor_ketinggian
	mac_pub = sha2.hmac_sha256("key_publisher", group_data_sensor)
	
	#json encoding
	array_data_sensor = [sensor_ketinggian, sensor_suhu, sensor_kekeruhan]
	dictionary_pub = {"mac" : str(mac_pub), "sensor" : array_data_sensor}
	json_pub = json.dumps(dictionary_pub)
	#print (dictionary_pub)
	
	#mqtt publish
	mqttc.publish("/node/Sensor", payload=json_pub)
	print("Published")
	#print ("mac = " + str(mac_pub) + "\ndata = {" + "kekeruhan : " + sensor_kekeruhan + " suhu : " + sensor_suhu + " ketinggian : " + sensor_ketinggian + "}\n")
	time.sleep(1)