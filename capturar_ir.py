from machine import Pin
import time

RECV_PIN = 15
receiver = Pin(RECV_PIN, Pin.IN)

def capturar_sinal_ir():
    pulsos = []
    start = time.ticks_us()
    while time.ticks_diff(time.ticks_us(), start) < 1_000_000:
        try:
            if receiver.value() == 0:
                pulso_inicio = time.ticks_us()
                while receiver.value() == 0:
                    pass
                pulso_duracao = time.ticks_diff(time.ticks_us(), pulso_inicio)
                pulsos.append(pulso_duracao)
        except Exception as e:
            print("Erro na captura do sinal IR:", e)
            break

    if not pulsos:
        print("Nenhum sinal IR capturado.")
    else:
        print("Sinal IR capturado:", pulsos)
    return pulsos

while True:
    print("Aguardando sinal IR...")
    capturar_sinal_ir()
    time.sleep(1)
