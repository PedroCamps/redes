import socket
import json
import time
import protocol
from protocol import Segmento, Pacote, Quadro, enviar_pela_rede_ruidosa

CLIENT_IP = "127.0.0.1"
CLIENT_PORT = 8080
MY_VIP = "CLIENTE_A"

DEST_VIP = "SERVIDOR"

ROUTER_ADDRESS = ("127.0.0.1", 6000)

TIMEOUT_ACK = 3.0

def main():
    print(f"--- CLIENTE INICIADO ({CLIENT_IP}:{CLIENT_PORT}) ---")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((CLIENT_IP, CLIENT_PORT))

    sock.settimeout(TIMEOUT_ACK)

    seq_num = 0

    print("Digite sua mensagem e tecle ENTER para enviar.")

    while True:
        try:
            msg = input(f"[{MY_VIP}] > ")
            if not msg: continue

            ack_recebido = False

            while not ack_recebido:
                segmento = Segmento(
                    seq_num=seq_num,
                    is_ack=False,
                    payload={"sender": MY_VIP, "message": msg, "timestamp": time.time()}
                )

                pacote = Pacote(
                    src_vip=MY_VIP,
                    dst_vip=DEST_VIP,
                    ttl=5,
                    segmento_dict=segmento.to_dict()
                )

                quadro = Quadro(
                    src_mac=f"MAC_{MY_VIP}",
                    dst_mac="MAC_ROUTER",
                    pacote_dict=pacote.to_dict()
                )

                bytes_envio = quadro.serializar()

                print(f"   [TRANS] Enviando SEQ={seq_num} ({len(bytes_envio)} bytes)...")
                enviar_pela_rede_ruidosa(sock, bytes_envio, ROUTER_ADDRESS)

                try:
                    print("   [TRANS] Aguardando ACK...")
                    data, addr = sock.recvfrom(4096)

                    q_recv, valido = Quadro.deserializar(data)
                    if not valido:
                        print("   [ERRO] ACK corrompido (CRC falhou). Retransmitindo...")
                        continue

                    p_recv = q_recv["data"]
                    if p_recv["dst_vip"] != MY_VIP:
                        print("   [ERRO] Recebi pacote de outro destino. Ignorando.")
                        continue

                    s_recv = p_recv["data"]
                    if s_recv["is_ack"] and s_recv["seq_num"] == seq_num:
                        print(f"   [SUCESSO] ACK {seq_num} Recebido! Mensagem entregue.")
                        ack_recebido = True
                    else:
                        print(f"   [ERRO] Recebi ACK incorreto (Seq={s_recv['seq_num']}). Esperava {seq_num}.")

                except socket.timeout:
                    print("   [TIMEOUT] ACK não chegou a tempo. Retransmitindo pacote...")

            seq_num = 1 - seq_num

        except KeyboardInterrupt:
            print("\nEncerrando cliente.")
            break
        except Exception as e:
            print(f"[ERRO CLIENTE] {e}")

if __name__ == "__main__":
    main()
