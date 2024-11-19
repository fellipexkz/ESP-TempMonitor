import time
import network
import machine
from machine import Pin, I2C
from lib import ssd1306
from lib import urequests
from lib.dht import DHT22
from config import nome_wifi, senha_wifi, chave_thingspeak

DHTPIN = 4
INTERVALO_DE_LEITURA_NORMAL = 600
INTERVALO_DE_LEITURA_ERRO = 60
I2C_ADDR = 0x3C
I2C_SCL_PIN = 22
I2C_SDA_PIN = 21
DISPLAY_WIDTH = 128
DISPLAY_HEIGHT = 64
THINGSPEAK_URL = f'https://api.thingspeak.com/update?api_key={chave_thingspeak}'

dht = DHT22(Pin(DHTPIN))
i2c = I2C(0, scl=Pin(I2C_SCL_PIN), sda=Pin(I2C_SDA_PIN))
display = ssd1306.SSD1306_I2C(DISPLAY_WIDTH, DISPLAY_HEIGHT, i2c)

SEND_PIN = 18
emissor = Pin(SEND_PIN, Pin.OUT)

codigo_ir_ligar = [4500, 4500, 500, 1600, 500, 500, 500, 1600]
codigo_ir_desligar = [4500, 4500, 500, 1600, 500, 500, 500, 500]


def configurar_display():
    display.fill(0)
    display.text("Teste do sensor DHT", 0, 0)
    print('Teste do sensor DHT')
    display.show()
    time.sleep(3)


def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        exibir_mensagem_display("Conectando ao WiFi...")
        print("Conectando ao WiFi...")
        wlan.connect(nome_wifi, senha_wifi)
        for _ in range(10):
            if wlan.isconnected():
                break
            time.sleep(1)
        if not wlan.isconnected():
            raise Exception("Falha ao conectar ao WiFi")
    exibir_mensagem_display(f"Conectado ao WiFi!\nIP: {wlan.ifconfig()[0]}")
    print("Conectado ao WiFi!")
    print("IP:", wlan.ifconfig()[0])
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


def exibir_dados_display(umidade, temperatura, status_envio, ac_status=""):
    display.fill(0)
    display.text(status_envio, 0, 0)
    display.hline(0, 12, 128, 1)
    display.text(f"Temp: {temperatura:.1f} C", 0, 20)
    display.text(f"Umid: {umidade:.1f} %", 0, 30)
    display.hline(0, 50, 128, 1)
    display.text(ac_status, 0, 55)
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
                return True
            response.close()
        except Exception as e:
            print(f"Erro ao enviar dados (tentativa {attempt + 1}): {e}")
        time.sleep(5)
    reiniciar_esp("Erro fatal! Reiniciando...")
    return False


def verificar_conexao_wifi():
    return network.WLAN(network.STA_IF).isconnected()


def reiniciar_esp(mensagem):
    exibir_mensagem_display(mensagem)
    time.sleep(3)
    machine.reset()


def inicializar_sistema():
    configurar_display()
    conectar_wifi()


def transmitir_sinal_ir(pulsos):
    for pulso in pulsos:
        emissor.on()
        time.sleep_us(pulso)
        emissor.off()
        time.sleep_us(500)


def controlar_ar_condicionado(temperatura):
    if temperatura >= 30:
        print("Temperatura alta. Ligando ar-condicionado...")
        transmitir_sinal_ir(codigo_ir_ligar)
        return "A/C Ligado"
    elif temperatura <= 25:
        print("Temperatura baixa. Desligando ar-condicionado...")
        transmitir_sinal_ir(codigo_ir_desligar)
        return "A/C Desligado"
    else:
        print('Temperatura normal. Monitorando...')
        return "Monitorando..."


inicializar_sistema()

intervalo_de_leitura = INTERVALO_DE_LEITURA_NORMAL if verificar_conexao_wifi() else INTERVALO_DE_LEITURA_ERRO

while True:
    umidade, temperatura = ler_sensor()
    if umidade is None or temperatura is None:
        exibir_dados_display(0, 0, "Erro no sensor!", "")
        time.sleep(2)
        continue

    print(f"Temperatura: {temperatura} °C, Umidade: {umidade} %")

    if enviar_thingspeak(temperatura, umidade):
        ac_status = controlar_ar_condicionado(temperatura)
    else:
        ac_status = "Erro ao enviar!"

    exibir_dados_display(umidade, temperatura, "Dados enviados!", ac_status)

    if not verificar_conexao_wifi():
        conectar_wifi()

    time.sleep(intervalo_de_leitura)
