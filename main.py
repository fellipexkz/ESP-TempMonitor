import time
import network
from machine import Pin, I2C
import ssd1306
import urequests
from dht import DHT22

DHTPIN = 4
dht = DHT22(Pin(DHTPIN))

I2C_ADDR = 0x3C
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
display = ssd1306.SSD1306_I2C(128, 64, i2c)

nome = "ZTE"
senha = "ViyGuMe885Nf"
apiKey = "Y0ZCIXD17CAV80TV"
url = f'https://api.thingspeak.com/update?api_key={apiKey}'


def configurar_display():
    if not display:
        raise Exception("Falha ao inicializar o display.")

    display.fill(0)
    display.text("Teste do sensor DHT", 0, 0)
    display.show()
    time.sleep(3)


def conectar_wifi():
    display.fill(0)
    display.text("Conectando ao WiFi...", 0, 0)
    display.show()

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(nome, senha)

    while not wlan.isconnected():
        time.sleep(1)

    display.fill(0)
    display.text("Conectado ao WiFi!", 0, 0)
    display.text("IP: {}".format(wlan.ifconfig()[0]), 0, 20)
    display.show()
    time.sleep(3)


def ler_sensor():
    dht.measure()
    temperatura = dht.temperature()
    umidade = dht.humidity()
    return umidade, temperatura


def exibir_dados_display(umidade, temperatura, status):
    display.fill(0)  # Limpa o display

    display.text(status, 0, 0)  # Exibe o status na linha 0
    display.hline(0, 12, 128, 1)  # Desenha uma linha horizontal na linha 12

    display.text("Temp: {:.1f} C".format(temperatura), 0, 20)  # Exibe a temperatura na linha 20
    display.text("Umid: {:.1f} %".format(umidade), 0, 40)  # Exibe a umidade na linha 40

    display.show()  # Atualiza o display


def enviar_thingspeak(temperatura, umidade):
    display.fill(0)
    display.text("Enviando dados...", 0, 0)
    display.show()
    response = urequests.get(url + f'&field1={temperatura}&field2={umidade}')

    if response.status_code == 200:
        print("Dados enviados com sucesso!")
        exibir_dados_display(umidade, temperatura, "Dados enviados!")
    else:
        print("Erro ao enviar os dados:", response.status_code)
        exibir_dados_display(umidade, temperatura, "Erro ao enviar!")

    response.close()


configurar_display()
conectar_wifi()

while True:
    umidade, temperatura = ler_sensor()

    if umidade is None or temperatura is None:
        exibir_dados_display(0, 0, "Erro no sensor!")
        time.sleep(2)
        continue

    print("Temperatura:", temperatura, "°C")
    print("Umidade:", umidade, "%")

    enviar_thingspeak(temperatura, umidade)

    time.sleep(30)
