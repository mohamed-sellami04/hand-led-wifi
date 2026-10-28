#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>

const char *WIFI_NAME = "Aaa";
const char *WIFI_PASSWORD = "00000000";

// Thumb, index, middle, ring, little finger
const int LED_PINS[] = {18, 19, 21, 22, 23};

WebServer server(80);
unsigned long lastCommand = 0;

void allOff()
{
  for (int pin : LED_PINS)
  {
    digitalWrite(pin, LOW);
  }
}

void handleLEDs()
{
  String state = server.arg("state");

  if (state.length() != 5)
  {
    server.send(400, "text/plain", "Send five bits, such as 01100");
    return;
  }

  for (int i = 0; i < 5; i++)
  {
    if (state[i] != '0' && state[i] != '1')
    {
      server.send(400, "text/plain", "Only 0 and 1 are allowed");
      return;
    }
  }

  for (int i = 0; i < 5; i++)
  {
    digitalWrite(LED_PINS[i], state[i] == '1' ? HIGH : LOW);
  }

  lastCommand = millis();
  server.send(200, "text/plain", state);
}

void setup()
{
  Serial.begin(115200);

  for (int pin : LED_PINS)
  {
    pinMode(pin, OUTPUT);
  }
  allOff();

  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  WiFi.begin(WIFI_NAME, WIFI_PASSWORD);

  Serial.print("Connecting");
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.print("ESP32 IP: ");
  Serial.println(WiFi.localIP());

  server.on("/", HTTP_GET, []()
            { server.send(200, "text/plain", "ESP32 LED controller is ready"); });

  server.on("/leds", HTTP_GET, handleLEDs);
  server.begin();
}

void loop()
{
  server.handleClient();

  // Switch off if commands stop arriving.
  if (WiFi.status() != WL_CONNECTED ||
      millis() - lastCommand > 2000)
  {
    allOff();
  }
}