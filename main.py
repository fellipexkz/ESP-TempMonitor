import time
import network
import machine
from machine import Pin, I2C
import ssd1306
import urequests
from dht import DHT22

DHTPIN = 4
INTERVALO_DE_LEITURA_NORMAL = 600
INTERVALO_DE_LEITURA_ERRO = 60
I2C_ADDR = 0x3C
I2C_SCL_PIN = 22
I2C_SDA_PIN = 21
DISPLAY_WIDTH = 128
DISPLAY_HEIGHT = 64
WIFI_SSID = "ZTE"
WIFI_PASSWORD = "ViyGuMe885Nf"
THINGSPEAK_API_KEY = "Y0ZCIXD17CAV80TV"
THINGSPEAK_URL = f'https://api.thingspeak.com/update?api_key={THINGSPEAK_API_KEY}'

dht = DHT22(Pin(DHTPIN))
i2c = I2C(0, scl=Pin(I2C_SCL_PIN), sda=Pin(I2C_SDA_PIN))
display = ssd1306.SSD1306_I2C(DISPLAY_WIDTH, DISPLAY_HEIGHT, i2c)


def configurar_display():
    display.fill(0)
    display.text("Teste do sensor DHT", 0, 0)
    display.show()
    time.sleep(3)


def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        exibir_mensagem_display("Conectando ao WiFi...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        for _ in range(10):
            if wlan.isconnected():
                break
            time.sleep(1)
        if not wlan.isconnected():
            raise Exception("Falha ao conectar ao WiFi")
    exibir_mensagem_display(f"Conectado ao WiFi!\nIP: {wlan.ifconfig()[0]}")
    time.sleep(3)


def ler_sensor():
    for attempt in range(3):
        try:
            dht.measure()
            temperatura = dht.temperature()
            umidade = dht.humidity()
            if temperatura is not None and umidade is not None:
                return umidade, temperatura
        except Exception as e:
            print(f"Erro ao ler o sensor (tentativa {attempt + 1}):", e)
            time.sleep(2)
    reiniciar_esp("Erro sensor! Reiniciando...")


def exibir_dados_display(umidade, temperatura, status):
    display.fill(0)
    display.text(status, 0, 0)
    display.hline(0, 12, 128, 1)
    display.text(f"Temp: {temperatura:.1f} C", 0, 20)
    display.text(f"Umid: {umidade:.1f} %", 0, 40)
    display.show()


def exibir_mensagem_display(mensagem):
    display.fill(0)
    for i, linha in enumerate(mensagem.split('\n')):
        display.text(linha, 0, i * 10)
    display.show()


def enviar_thingspeak(temperatura, umidade):
    exibir_mensagem_display("Enviando dados...")
    for attempt in range(5):
        try:
            if not verificar_conexao_wifi():
                conectar_wifi()
            response = urequests.get(f'{THINGSPEAK_URL}&field1={temperatura}&field2={umidade}', timeout=5)
            if response.status_code == 200:
                print("Dados enviados com sucesso!")
                exibir_dados_display(umidade, temperatura, "Dados enviados!")
                response.close()
                return
        except Exception as e:
            print(f"Erro ao enviar dados (tentativa {attempt + 1}): {e}")
        time.sleep(5)
    reiniciar_esp("Erro fatal! Reiniciando...")


def verificar_conexao_wifi():
    return network.WLAN(network.STA_IF).isconnected()


def reiniciar_esp(mensagem):
    exibir_mensagem_display(mensagem)
    time.sleep(3)
    machine.reset()


def inicializar_sistema():
    configurar_display()
    conectar_wifi()


inicializar_sistema()

while True:
    if not verificar_conexao_wifi():
        conectar_wifi()
        intervalo_de_leitura = INTERVALO_DE_LEITURA_ERRO
    else:
        intervalo_de_leitura = INTERVALO_DE_LEITURA_NORMAL

    umidade, temperatura = ler_sensor()
    if umidade is None or temperatura is None:
        exibir_dados_display(0, 0, "Erro no sensor!")
        time.sleep(2)
        continue

    print(f"Temperatura: {temperatura} °C, Umidade: {umidade} %")
    enviar_thingspeak(temperatura, umidade)
    time.sleep(intervalo_de_leitura)


"""
# Código do receptor IR
RECV_PIN = 15
receiver = Pin(RECV_PIN, Pin.IN)

def capturar_sinal_ir():
    pulsos = []
    start = time.ticks_us()
    while time.ticks_diff(time.ticks_us(), start) < 1_000_000:
        if receiver.value() == 0:
            pulso_inicio = time.ticks_us()
            while receiver.value() == 0:
                pass
            pulso_duracao = time.ticks_diff(time.ticks_us(), pulso_inicio)
            pulsos.append(pulso_duracao)

    print("Sinal IR capturado:", pulsos)
    return pulsos

while True:
    print("Aguardando sinal IR...")
    capturar_sinal_ir()
    time.sleep(1)
"""

"""
# Código do emissor IR
SEND_PIN = 2
emissor = Pin(SEND_PIN, Pin.OUT)

codigo_ir_ligar = []
codigo_ir_desligar = []

def transmitir_sinal_ir(pulsos):
    for pulso in pulsos:
        emissor.on()
        time.sleep_us(pulso)
        emissor.off()
        time.sleep_us(500)

def controlar_ar_condicionado(temperatura):
    if temperatura >= 25:
        print("Temperatura alta. Ligando ar-condicionado...")
        # Fazer a exibição no display também
        transmitir_sinal_ir(codigo_ir_ligar)
    elif temperatura <= 22:
        print("Temperatura baixa. Desligando ar-condicionado...")
        # Fazer a exibição no display também
        transmitir_sinal_ir(codigo_ir_desligar)
"""
