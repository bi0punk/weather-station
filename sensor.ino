#include <Ethernet.h>
#include <SPI.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <ArduinoJson.h>

#define ONE_WIRE_BUS 2

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
IPAddress ip(192, 168, 1, 100);
IPAddress server1(192, 168, 1, 129);
IPAddress server2(192, 168, 1, 87);
EthernetClient client;

unsigned long lastMillis = 0;
const unsigned long interval = 20000;

bool useFirstIP = true;

void setup() {
  Serial.begin(9600);
  sensors.begin();
  Ethernet.begin(mac, ip);
}

void loop() {
  if (millis() - lastMillis > interval) {
    lastMillis = millis();

    sensors.requestTemperatures();
    float tempC = sensors.getTempCByIndex(0);

    if (tempC != DEVICE_DISCONNECTED_C) {
      Serial.print("Temperatura: ");
      Serial.print(tempC);
      Serial.println(" C");

      StaticJsonDocument<64> jsonDocument;
      jsonDocument["temperature"] = tempC;

      String jsonString;
      serializeJson(jsonDocument, jsonString);

      Serial.println(jsonString);

      if (useFirstIP) {
        if (!client.connect(server1, 5000)) {
          useFirstIP = false;
        }
      } else {
        if (!client.connect(server2, 5000)) {
          useFirstIP = true;
        }
      }

      if (client.connected()) {
        Serial.println("Conectado al servidor");

        client.print("POST /sensor HTTP/1.1\r\n");
        client.print("Host: ");
        if (useFirstIP) {
          client.print(server1);
        } else {
          client.print(server2);
        }
        client.print("\r\n");
        client.print("Connection: close\r\n");
        client.print("Content-Type: application/json\r\n");
        client.print("Content-Length: ");
        client.print(jsonString.length());
        client.print("\r\n\r\n");
        client.print(jsonString);

        Serial.println(jsonString);
        Serial.println("Informacion enviada exitosamente");

        client.stop();
      } else {
        Serial.println("Error de conexion");
      }
    }
  }
}
