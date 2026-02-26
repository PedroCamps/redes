import socket
import json
import protocol
from protocol import Segmento, Pacote, Quadro, enviar_pela_rede_ruidosa

# Configurações do Servidor
SERVER_IP = "127.0.0.1"
SERVER_PORT = 9090
MY_VIP = "SERVIDOR"

# Configuração do Roteador (Gateway Padrão)
ROUTER_ADDRESS = ("127.0.0.1", 6000)

def main():
    print(f"--- SERVIDOR INICIADO ({SERVER_IP}:{SERVER_PORT}) ---")
    print(f"--- VIP: {MY_VIP} ---")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((SERVER_IP, SERVER_PORT))
    
    # Estado da Camada de Transporte
    # Esperamos o primeiro pacote com sequência 0
    expected_seq = 0
    
    while True:
        try:
            data, addr = sock.recvfrom(4096)
            
            # --- CAMADA 2: ENLACE ---
            quadro_dict, valido = Quadro.deserializar(data)
            if not valido:
                print("   [CAMADA 2] ERRO DE CRC! Ignorando.")
                continue
            
            # --- CAMADA 3: REDE ---
            pacote_dict = quadro_dict["data"]
            if pacote_dict["dst_vip"] != MY_VIP:
                print(f"   [CAMADA 3] Pacote para {pacote_dict['dst_vip']} ignorado. Sou {MY_VIP}.")
                continue
                
            src_vip = pacote_dict["src_vip"]
            segmento_dict = pacote_dict["data"]
            
            # --- CAMADA 4: TRANSPORTE ---
            seq_num = segmento_dict["seq_num"]
            is_ack = segmento_dict["is_ack"]
            payload = segmento_dict["payload"]
            
            if is_ack:
                print("   [CAMADA 4] Recebi um ACK perdido? Ignorando.")
                continue
                
            print(f"   [CAMADA 4] Recebido SEQ={seq_num}. Esperado={expected_seq}")
            
            if seq_num == expected_seq:
                # Pacote novo e correto!
                # --- CAMADA 5: APLICAÇÃO ---
                mensagem = payload.get("message", "")
                usuario = payload.get("sender", "Unknown")
                print(f"\n   [APLICAÇÃO] MENSAGEM DE {usuario}: {mensagem}\n")
                
                # Avança sequência esperada (0->1->0...)
                expected_seq = 1 - expected_seq
            else:
                # Duplicata (Já recebi 0, esperava 1, mas veio 0 de novo pq o ACK se perdeu)
                print("   [CAMADA 4] Duplicata detectada. Reenviando ACK.")

            # ENVIAR ACK (Para o Novo ou para a Duplicata)
            # O ACK deve ter o número de sequência do que foi RECEBIDO (confirmando ele)
            
            ack_segmento = Segmento(seq_num=seq_num, is_ack=True, payload={})
            
            ack_pacote = Pacote(
                src_vip=MY_VIP,
                dst_vip=src_vip, # Devolve para quem enviou
                ttl=5,
                segmento_dict=ack_segmento.to_dict()
            )
            
            ack_quadro = Quadro(
                src_mac=f"MAC_{MY_VIP}",
                dst_mac="MAC_ROUTER", # Sempre enviamos pro Router
                pacote_dict=ack_pacote.to_dict()
            )
            
            print(f"   [CAMADA 4] Enviando ACK {seq_num} para {src_vip} via Roteador.")
            enviar_pela_rede_ruidosa(sock, ack_quadro.serializar(), ROUTER_ADDRESS)
            
        except Exception as e:
            print(f"[ERRO NO SERVIDOR] {e}")

if __name__ == "__main__":
    main()
