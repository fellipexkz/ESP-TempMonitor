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

#define LARGURA_TELA 128
#define ALTURA_TELA 64
#define REINICIAR_OLED -1

Adafruit_SSD1306 display(LARGURA_TELA, ALTURA_TELA, &Wire, REINICIAR_OLED);
DHT dht(DHTPIN, DHTTYPE);

const char *nome = "ZTE";
const char *senha = "ViyGuMe885Nf";

const int channel = 2667623;
const char *apiKey = "Y0ZCIXD17CAV80TV";

WiFiClient cliente;

void configurarDisplay()
{
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C))
  {
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
}

void conectarWiFi()
{
  display.clearDisplay();
  display.setCursor(0, 0);
  display.println("Conectando ao WiFi...");
  display.display();

  Serial.println("Conectando ao WiFi...");
  WiFi.begin(nome, senha);
  while (WiFi.status() != WL_CONNECTED)
  {
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

void lerSensor(float &umidade, float &temperatura)
{
  umidade = dht.readHumidity();
  temperatura = dht.readTemperature();
}

void exibirDadosDisplay(float umidade, float temperatura, const char *status)
{
  display.clearDisplay();

  display.setTextSize(1);
  display.setCursor(0, 0);
  display.println(status);

  display.drawLine(0, 12, LARGURA_TELA, 12, WHITE);

  display.setTextSize(2);
  display.setCursor(0, 20);
  display.print("Temp: ");
  display.print(temperatura, 1);

  display.setCursor(0, 40);
  display.print("Umid: ");
  display.print(umidade, 1);

  display.display();
}

void enviarThingSpeak(float temperatura, float umidade)
{
  if (WiFi.status() != WL_CONNECTED)
  {
    conectarWiFi();
  }

  ThingSpeak.setField(1, temperatura);
  ThingSpeak.setField(2, umidade);
  int resposta = ThingSpeak.writeFields(channel, apiKey);

  const char *status;
  if (resposta == 200)
  {
    Serial.println("\nDados enviados com sucesso para o ThingSpeak!");
    status = "Dados enviados!";
  }
  else
  {
    Serial.println("\nErro ao enviar os dados. Código de erro: " + String(resposta));
    status = "Erro ao enviar!";
  }

  exibirDadosDisplay(umidade, temperatura, status);
}

void setup()
{
  Serial.begin(9600);
  dht.begin();
  Serial.println("Teste do sensor DHT");

  configurarDisplay();
  conectarWiFi();
  ThingSpeak.begin(cliente);
}

void loop()
{
  if (WiFi.status() != WL_CONNECTED)
  {
    conectarWiFi();
  }

  float umidade, temperatura;
  lerSensor(umidade, temperatura);

  int tentativas = 0;
  while ((isnan(umidade) || isnan(temperatura)) && tentativas < 3)
  {
    Serial.println("Falha ao ler sensor DHT, tentando novamente...");
    delay(2000);
    lerSensor(umidade, temperatura);
    tentativas++;
  }

  if (isnan(umidade) || isnan(temperatura))
  {
    Serial.println("Falha ao ler sensor DHT após 3 tentativas!");
    display.clearDisplay();
    display.setCursor(0, 0);
    display.println("Falha ao ler sensor DHT!");
    display.display();
    return;
  }

  Serial.print("Temperatura: ");
  Serial.print(temperatura);
  Serial.println(" °C");
  Serial.print("Umidade: ");
  Serial.print(umidade);
  Serial.print(" %\t");

  enviarThingSpeak(temperatura, umidade);

  delay(600000);
}
