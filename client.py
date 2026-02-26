import socket
import json
import time
import protocol
from protocol import Segmento, Pacote, Quadro, enviar_pela_rede_ruidosa

# Configurações do Cliente
CLIENT_IP = "127.0.0.1"
CLIENT_PORT = 8080
MY_VIP = "CLIENTE_A"

# Destino (Queremos falar com o Servidor)
DEST_VIP = "SERVIDOR"

# Configuração do Roteador (Gateway Padrão)
ROUTER_ADDRESS = ("127.0.0.1", 6000)

# Timeout para retransmissão (segundos)
TIMEOUT_ACK = 3.0

def main():
    print(f"--- CLIENTE INICIADO ({CLIENT_IP}:{CLIENT_PORT}) ---")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((CLIENT_IP, CLIENT_PORT))
    
    # Define timeout no socket para esperar o ACK
    sock.settimeout(TIMEOUT_ACK)
    
    seq_num = 0 # Começa com 0
    
    print("Digite sua mensagem e tecle ENTER para enviar.")
    
    while True:
        try:
            msg = input(f"[{MY_VIP}] > ")
            if not msg: continue
            
            # --- ENVIO STOP-AND-WAIT ---
            ack_recebido = False
            
            while not ack_recebido:
                # 1. Monta a Pilha de Protocolos
                
                # Camada 4: Transporte
                segmento = Segmento(
                    seq_num=seq_num,
                    is_ack=False,
                    payload={"sender": MY_VIP, "message": msg, "timestamp": time.time()}
                )
                
                # Camada 3: Rede
                pacote = Pacote(
                    src_vip=MY_VIP,
                    dst_vip=DEST_VIP,
                    ttl=5, # Time to Live
                    segmento_dict=segmento.to_dict()
                )
                
                # Camada 2: Enlace
                quadro = Quadro(
                    src_mac=f"MAC_{MY_VIP}",
                    dst_mac="MAC_ROUTER", # Próximo salto é o roteador
                    pacote_dict=pacote.to_dict()
                )
                
                # Serializa (JSON + CRC)
                bytes_envio = quadro.serializar()
                
                # Envia
                print(f"   [TRANS] Enviando SEQ={seq_num} ({len(bytes_envio)} bytes)...")
                enviar_pela_rede_ruidosa(sock, bytes_envio, ROUTER_ADDRESS)
                
                # Espera ACK
                try:
                    print("   [TRANS] Aguardando ACK...")
                    data, addr = sock.recvfrom(4096)
                    
                    # --- PROCESSA RESPOSTA ---
                    
                    # LINK CHECK
                    q_recv, valido = Quadro.deserializar(data)
                    if not valido:
                        print("   [ERRO] ACK corrompido (CRC falhou). Retransmitindo...")
                        continue # Retenta loop while
                        
                    # NETWORK CHECK
                    p_recv = q_recv["data"]
                    if p_recv["dst_vip"] != MY_VIP:
                        print("   [ERRO] Recebi pacote de outro destino. Ignorando.")
                        continue
                        
                    # TRANSPORT CHECK
                    s_recv = p_recv["data"]
                    if s_recv["is_ack"] and s_recv["seq_num"] == seq_num:
                        print(f"   [SUCESSO] ACK {seq_num} Recebido! Mensagem entregue.")
                        ack_recebido = True
                    else:
                        print(f"   [ERRO] Recebi ACK incorreto (Seq={s_recv['seq_num']}). Esperava {seq_num}.")
                        # Se recebeu ACK errado (ex: duplicado antigo), ignora e o timeout vai estourar se o correto não vier, 
                        # ou loop continua esperando.
                        # Mas como o socket recv consome, precisamos voltar a esperar ou reenviar.
                        # No Stop-and-Wait simples, se receber algo errado, o ideal seria continuar esperando no mesmo socket recv,
                        # mas aqui nosso while reimprime o envio. Isso é "Retransmissão Precoce" se falhar o check.
                        # Vamos aceitar isso por simplicidade.
                
                except socket.timeout:
                    print("   [TIMEOUT] ACK não chegou a tempo. Retransmitindo pacote...")
            
            # Próximo número de sequência
            seq_num = 1 - seq_num
            
        except KeyboardInterrupt:
            print("\nEncerrando cliente.")
            break
        except Exception as e:
            print(f"[ERRO CLIENTE] {e}")

if __name__ == "__main__":
    main()
