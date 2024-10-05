#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <DHT_U.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <WiFi.h>
#include <ThingSpeak.h>

#define DHTPIN 4
#define DHTTYPE DHT22

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

DHT dht(DHTPIN, DHTTYPE);

const char* WIFI_NAME = "ZTE";
const char* WIFI_PASSWORD = "ViyGuMe885Nf";

const int myChannelNumber = 2667623;
const char* myApiKey = "Y0ZCIXD17CAV80TV";

WiFiClient client;

void conectarWiFi() {
  display.clearDisplay();
  display.setCursor(0, 0);
  display.println("Conectando ao WiFi...");
  display.display();

  Serial.println("Conectando ao WiFi...");
  WiFi.begin(WIFI_NAME, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }

  Serial.println("\nConectado ao WiFi!");
  display.clearDisplay();
  display.setCursor(0, 0);
  display.println("Conectado ao WiFi!");
  display.print("IP: ");
  display.println(WiFi.localIP());
  display.display();
  delay(3000);
}

void setup() {
  Serial.begin(9600);
  dht.begin();
  Serial.println("Teste do sensor DHT");
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("Falha ao inicializar o display SSD1306"));
    for (;;)
      ;
  }
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(0, 0);
  display.println("Teste do sensor DHT");
  display.display();
  delay(3000);

  conectarWiFi();
  ThingSpeak.begin(client);
}

void loop() {
  delay(2000);

  float h = dht.readHumidity();
  float t = dht.readTemperature();

  if (isnan(h) || isnan(t)) {
    Serial.println("Falha ao ler sensor DHT!");
    display.clearDisplay();
    display.setCursor(0, 0);
    display.println("Falha ao ler sensor DHT!");
    display.display();
    return;
  }

  Serial.print("Umidade: ");
  Serial.print(h);
  Serial.print(" %\t");
  Serial.print("Temperatura: ");
  Serial.print(t);
  Serial.println(" Â°C");

  display.clearDisplay();
  display.setCursor(0, 0);
  display.print("Umidade: ");
  display.print(h, 1);
  display.println(" %");
  display.print("Temperatura: ");
  display.print(t, 1);
  display.println(" C");

  ThingSpeak.setField(1, t);
  ThingSpeak.setField(2, h);
  int response = ThingSpeak.writeFields(myChannelNumber, myApiKey);

  display.setCursor(0, 50);
  if (response == 200) {
    Serial.println("Dados enviados com sucesso para o ThingSpeak!");
    display.println("Dados enviados!");
  } else {
    Serial.println("Erro ao enviar os dados. Código de erro: " + String(response));
    display.println("Erro ao enviar!");
  }

  display.display();
  delay(600000);
}
