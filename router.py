import socket
import json
import sys
import protocol
from protocol import Quadro, Pacote, enviar_pela_rede_ruidosa

ROUTER_IP = "127.0.0.1"
ROUTER_PORT = 6000

ROUTING_TABLE = {
    "CLIENTE_A": ("127.0.0.1", 8080),
    "SERVIDOR": ("127.0.0.1", 9090),
}

def main():
    print(f"--- ROTEADOR INICIADO ({ROUTER_IP}:{ROUTER_PORT}) ---")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ROUTER_IP, ROUTER_PORT))

    while True:
        try:
            data, addr = sock.recvfrom(4096)
            print(f"\n[ROUTER] Recebido {len(data)} bytes de {addr}")

            quadro_dict, valido = Quadro.deserializar(data)

            if not valido:
                print("   [CAMADA 2] ERRO DE CRC! Quadro descartado silenciosamente.")
                continue

            print("   [CAMADA 2] Quadro Íntegro (CRC OK).")

            pacote_dict = quadro_dict["data"]

            dst_vip = pacote_dict["dst_vip"]
            ttl = pacote_dict["ttl"]

            print(f"   [CAMADA 3] Destino: {dst_vip} | TTL: {ttl}")

            pacote_dict["ttl"] -= 1

            if pacote_dict["ttl"] <= 0:
                print("   [CAMADA 3] TTL Expirado após decremento! Pacote descartado.")
                continue

            if dst_vip in ROUTING_TABLE:
                proximo_salto_ip, proximo_salto_port = ROUTING_TABLE[dst_vip]
                dest_addr = (proximo_salto_ip, proximo_salto_port)

                print(f"   [CAMADA 3] Encaminhando para {dst_vip} -> {dest_addr}")

                novo_quadro = Quadro(
                    src_mac="MAC_ROUTER",
                    dst_mac=f"MAC_{dst_vip}",
                    pacote_dict=pacote_dict
                )

                bytes_para_enviar = novo_quadro.serializar()

                enviar_pela_rede_ruidosa(sock, bytes_para_enviar, dest_addr)

            else:
                print(f"   [CAMADA 3] Destino {dst_vip} desconhecido! Descartando.")

        except Exception as e:
            print(f"[ERRO NO ROTEADOR] {e}")

if __name__ == "__main__":
    main()
