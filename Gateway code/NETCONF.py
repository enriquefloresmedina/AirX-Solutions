from umqtt.robust import MQTTClient
import network

def wifi_connect(SSID, PASSWORD):
    global sta_if

    sta_if = network.WLAN(network.STA_IF)
    
    if not sta_if.isconnected():
        print('Connecting to WIFI network...')
        sta_if.active(True)
        sta_if.connect(SSID, PASSWORD)
        while not sta_if.isconnected():
            pass
    print('Connected to WIFI!')

def mqtt_connect():
    global mqtt_client, mqtt_topic
    
    certificate_file = "/2f9a209bc84e9517f80f7d89d929a7d7f08d16118b7466195dd23a5ad42aadeb-certificate.pem.crt"
    private_key_file = "/2f9a209bc84e9517f80f7d89d929a7d7f08d16118b7466195dd23a5ad42aadeb-private.pem.key"
    mqtt_client_id = "esp32"
    mqtt_port = 8883
    mqtt_topic = "esp32/publish"
    mqtt_host = "adi9qgij6bpmb-ats.iot.us-east-2.amazonaws.com"
    with open(private_key_file, "r") as f:
        private_key = f.read()

    with open(certificate_file, "r") as f:
        certificate = f.read()

    mqtt_client = MQTTClient(client_id=mqtt_client_id, server=mqtt_host, port=mqtt_port, keepalive=5000, ssl=True, ssl_params={"cert":certificate, "key":private_key, "server_side":False})

    if not sta_if.isconnected():
        print('Connect to a wifi network first!')
    else:
        print('Connecting to MQTT client...')
        mqtt_client.connect()
        print('Connected to MQTT client!')

def mqtt_publish(message):
    mqtt_client.publish(mqtt_topic, message)
    print("Message published to", mqtt_topic)
    
    
def wifi_disconnect():
    print('Disconnecting WIFI network...')
    sta_if.disconnect()
    while sta_if.isconnected():
            pass
    print('Disconnected from WIFI')
    sta_if.active(False)
