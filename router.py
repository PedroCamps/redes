import socket
import json
import sys
import protocol
from protocol import Quadro, Pacote, enviar_pela_rede_ruidosa

# Configuração do Roteador
ROUTER_IP = "127.0.0.1"
ROUTER_PORT = 6000 # Porta física do roteador

# Tabela de Roteamento (Estática)
# Mapeia VIP (Virtual IP) -> (IP Físico, Porta Física)
ROUTING_TABLE = {
    "CLIENTE_A": ("127.0.0.1", 8080), # Cliente
    "SERVIDOR": ("127.0.0.1", 9090),  # Servidor
}

def main():
    print(f"--- ROTEADOR INICIADO ({ROUTER_IP}:{ROUTER_PORT}) ---")
    
    # Cria o socket UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ROUTER_IP, ROUTER_PORT))
    
    while True:
        try:
            # Recebe dados
            data, addr = sock.recvfrom(4096)
            print(f"\n[ROUTER] Recebido {len(data)} bytes de {addr}")
            
            # --- CAMADA 2: ENLACE ---
            # Deserializa e verifica CRC
            quadro_dict, valido = Quadro.deserializar(data)
            
            if not valido:
                print("   [CAMADA 2] ERRO DE CRC! Quadro descartado silenciosamente.")
                continue # Descarta
                
            print("   [CAMADA 2] Quadro Íntegro (CRC OK).")
            
            # Extrai o Pacote (Payload do Quadro)
            pacote_dict = quadro_dict["data"]
            
            # --- CAMADA 3: REDE ---
            # Reconstrói o objeto Pacote (apenas para acesso fácil, ou usa dict direto)
            # Como a classe Pacote é simples, vamos manipular o dict ou instanciar
            # Vamos instanciar para usar a lógica de TTL se houvesse métodos, mas aqui é direto
            
            dst_vip = pacote_dict["dst_vip"]
            ttl = pacote_dict["ttl"]

            print(f"   [CAMADA 3] Destino: {dst_vip} | TTL: {ttl}")

            # Decrementa TTL primeiro
            pacote_dict["ttl"] -= 1

            # Verifica se expirou após decremento
            if pacote_dict["ttl"] <= 0:
                print("   [CAMADA 3] TTL Expirado após decremento! Pacote descartado.")
                continue
            
            # Busca na Tabela de Roteamento
            if dst_vip in ROUTING_TABLE:
                proximo_salto_ip, proximo_salto_port = ROUTING_TABLE[dst_vip]
                dest_addr = (proximo_salto_ip, proximo_salto_port)
                
                print(f"   [CAMADA 3] Encaminhando para {dst_vip} -> {dest_addr}")
                
                # Re-encapsula no Quadro (Necessário pois TTL mudou o payload)
                # O MAC de origem agora é o do Roteador, Destino é o Next Hop (fictício aqui)
                # Mantemos o MAC original ou trocamos? Na teoria troca.
                # Vamos simplificar e criar um novo Quadro.
                
                novo_quadro = Quadro(
                    src_mac="MAC_ROUTER", 
                    dst_mac=f"MAC_{dst_vip}", 
                    pacote_dict=pacote_dict
                )
                
                bytes_para_enviar = novo_quadro.serializar()
                
                # Envia usando o simulador de ruído
                enviar_pela_rede_ruidosa(sock, bytes_para_enviar, dest_addr)
                
            else:
                print(f"   [CAMADA 3] Destino {dst_vip} desconhecido! Descartando.")

        except Exception as e:
            print(f"[ERRO NO ROTEADOR] {e}")

if __name__ == "__main__":
    main()
