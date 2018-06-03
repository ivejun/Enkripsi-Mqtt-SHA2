import json
import sha2
# Import library paho-mqtt
import paho.mqtt.client as mqtt

# Inisiasi object mqtte
mqttc = mqtt.Client("sub1", clean_session=True)

# Buat koneksi ke broker
mqttc.connect( "192.168.201.100", 1883 )

def on_connect(mqttc, obj, flags, rc):
	print("Connected")

def on_message(mqttc, obj, msg):
	#json encoding
	data_str = json.loads(str(msg.payload.decode("utf-8")))
	mac_pub = data_str["mac"]
	data_sensor = data_str["sensor"]
	
	#baca array dalam json
	data_sensor_ketinggian = data_sensor[0]
	data_sensor_suhu = data_sensor[1]
	data_sensor_kekeruhan = data_sensor[2]
	
	#string sensor 1 + sensor 2 + sensor 3
	group_data_sensor = data_sensor_kekeruhan + data_sensor_suhu + data_sensor_ketinggian
	mac_sub = sha2.hmac_sha256("key_publisher", group_data_sensor)
	
	if (str(mac_sub) == mac_pub) :
		print ("mac = " + str(mac_pub) + "\ndata = {" + "kekeruhan : " + data_sensor_kekeruhan + " suhu : " + data_sensor_suhu + " ketinggian : " + data_sensor_ketinggian + "}\n")
	else :
		print ("data tidak valid")

# Set callback function
mqttc.on_connect = on_connect
mqttc.on_message = on_message

# Subscribe ke topik tertentu
mqttc.subscribe("/node/Sensor", qos=1)

# Loop supaya subscribernya tidak berhenti
mqttc.loop_forever()
