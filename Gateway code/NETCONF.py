from umqtt.robust import MQTTClient
import network, time

def wifi_init():
    global sta_if
    sta_if = network.WLAN(network.STA_IF)

def mqtt_init():
    global mqtt_client, mqtt_topic
    
    certificate_file = "/2f9a209bc84e9517f80f7d89d929a7d7f08d16118b7466195dd23a5ad42aadeb-certificate.pem.crt"
    private_key_file = "/2f9a209bc84e9517f80f7d89d929a7d7f08d16118b7466195dd23a5ad42aadeb-private.pem.key"
    mqtt_client_id = "esp32"
    mqtt_port = 8883
    mqtt_topic = "esp32/publish"
    mqtt_host = "adi9qgij6bpmb-ats.iot.us-east-2.amazonaws.com"
    try:
        with open(private_key_file, "r") as f:
            private_key = f.read()
    except OSError:
        print('AWS certificates missing')

    with open(certificate_file, "r") as f:
        certificate = f.read()

    mqtt_client = MQTTClient(client_id=mqtt_client_id, server=mqtt_host, port=mqtt_port, keepalive=5000, ssl=True, ssl_params={"cert":certificate, "key":private_key, "server_side":False})

def mqtt_connect():
    if not sta_if.isconnected():
        print('Connect to a WIFI network first!')
    else:
        print('Connecting to MQTT client...')
        mqtt_client.connect()
        print('Connected to MQTT client!')

def mqtt_publish(message):
    mqtt_client.publish(mqtt_topic, message)
    print("Message published to", mqtt_topic)
    time.sleep(1)

def mqtt_disconnect():
    mqtt_client.disconnect()
    print('Disconnected from MQTT client!')

def wifi_connect(SSID, PASSWORD):
    global sta_if
    
    if not sta_if.isconnected():
        print('Connecting to WIFI network...')
        sta_if.active(True)
        sta_if.connect(SSID, PASSWORD)
        while not sta_if.isconnected():
            pass
    print('Connected to WIFI!')
    
def wifi_disconnect():
    if sta_if.isconnected(): 
        sta_if.disconnect()
        while sta_if.isconnected():
            pass
        sta_if.active(False)
    print('Disconnected from WIFI')
