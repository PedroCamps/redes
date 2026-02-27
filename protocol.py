import json
import zlib
import random
import time
import socket

PROBABILIDADE_PERDA = 0.2
PROBABILIDADE_CORRUPCAO = 0.2
LATENCIA_MIN = 0.1
LATENCIA_MAX = 0.5

class Segmento:
    def __init__(self, seq_num, is_ack, payload):
        self.seq_num = seq_num
        self.is_ack = is_ack
        self.payload = payload

    def to_dict(self):
        return {
            "seq_num": self.seq_num,
            "is_ack": self.is_ack,
            "payload": self.payload
        }

class Pacote:
    def __init__(self, src_vip, dst_vip, ttl, segmento_dict):
        self.src_vip = src_vip
        self.dst_vip = dst_vip
        self.ttl = ttl
        self.data = segmento_dict

    def to_dict(self):
        return {
            "src_vip": self.src_vip,
            "dst_vip": self.dst_vip,
            "ttl": self.ttl,
            "data": self.data
        }

class Quadro:
    def __init__(self, src_mac, dst_mac, pacote_dict):
        self.src_mac = src_mac
        self.dst_mac = dst_mac
        self.data = pacote_dict
        self.fcs = 0

    def serializar(self):
        dados_para_calculo = {
            "src_mac": self.src_mac,
            "dst_mac": self.dst_mac,
            "data": self.data,
            "fcs": 0
        }

        json_str = json.dumps(dados_para_calculo, sort_keys=True)
        bytes_dados = json_str.encode('utf-8')

        crc = zlib.crc32(bytes_dados)

        dados_finais = dados_para_calculo.copy()
        dados_finais['fcs'] = crc

        return json.dumps(dados_finais).encode('utf-8')

    @staticmethod
    def deserializar(bytes_recebidos):
        try:
            dados_dict = json.loads(bytes_recebidos.decode('utf-8'))

            fcs_recebido = dados_dict.get('fcs', 0)

            dados_para_calculo = dados_dict.copy()
            dados_para_calculo['fcs'] = 0

            json_str = json.dumps(dados_para_calculo, sort_keys=True)
            fcs_calculado = zlib.crc32(json_str.encode('utf-8'))

            if fcs_recebido == fcs_calculado:
                return dados_dict, True
            else:
                return dados_dict, False

        except (json.JSONDecodeError, UnicodeDecodeError):
            return None, False

def enviar_pela_rede_ruidosa(socket_udp, bytes_dados, endereco_destino):
    print(f"   [FÍSICA] Tentando transmitir {len(bytes_dados)} bytes...")

    if random.random() < PROBABILIDADE_PERDA:
        print("   [FÍSICA] O pacote foi perdido na rede (Drop).")
        return

    array_dados = bytearray(bytes_dados)

    if random.random() < PROBABILIDADE_CORRUPCAO:
        print("   [FÍSICA] Interferência eletromagnética! Bits trocados.")

        if len(array_dados) > 0:
            pos = random.randint(0, len(array_dados) - 1)
            array_dados[pos] = array_dados[pos] ^ 0xFF

    time.sleep(random.uniform(LATENCIA_MIN, LATENCIA_MAX))

    socket_udp.sendto(bytes(array_dados), endereco_destino)
    print("   [FÍSICA] Sinal enviado para o meio físico.")
