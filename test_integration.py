import subprocess
import time
import socket
import sys
import os
import signal

def run_verification():
    print("--- INICIANDO VERIFICAÇÃO AUTOMATIZADA ---")

    p_router = subprocess.Popen([sys.executable, "router.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print("Router iniciado...")
    time.sleep(1)

    p_server = subprocess.Popen([sys.executable, "server.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print("Servidor iniciado...")
    time.sleep(1)

    client_code = """
import socket
import time
import sys
sys.path.append(".")
from protocol import Segmento, Pacote, Quadro, enviar_pela_rede_ruidosa

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(5.0)
sock.bind(("127.0.0.1", 8080))
dest = ("127.0.0.1", 6000)

print("CLIENTE TEST: Enviando...")

seg = Segmento(0, False, {"sender": "TESTER", "message": "HELLO WORLD"})
pac = Pacote("CLIENTE_A", "SERVIDOR", 5, seg.to_dict())
qua = Quadro("MAC_A", "MAC_ROUTER", pac.to_dict())
data = qua.serializar()

while True:
    enviar_pela_rede_ruidosa(sock, data, dest)
    try:
        data, addr = sock.recvfrom(4096)
        print("CLIENTE TEST: Resposta recebida!")
        break
    except socket.timeout:
        print("CLIENTE TEST: Timeout...")
"""

    with open("test_client_temp.py", "w") as f:
        f.write(client_code)

    p_client = subprocess.Popen([sys.executable, "test_client_temp.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    try:
        stdout, stderr = p_client.communicate(timeout=15)
        print("--- SAÍDA DO CLIENTE TESTE ---")
        print(stdout)

        if "Resposta recebida!" in stdout:
            print(">>> SUCESSO: O ciclo completo (Envio -> Router -> Servidor -> ACK -> Router -> Cliente) funcionou!")
        else:
            print(">>> FALHA: Cliente não recebeu confirmação.")
            print("Stderr Cliente:", stderr)

    except subprocess.TimeoutExpired:
        p_client.kill()
        print(">>> FALHA: Timeout no teste de integração.")

    finally:
        os.kill(p_router.pid, signal.SIGTERM)
        os.kill(p_server.pid, signal.SIGTERM)

        out_r, err_r = p_router.communicate()
        out_s, err_s = p_server.communicate()

        print("\n--- LOG ROTEADOR (Últimas linhas) ---")
        print("\n".join(out_r.splitlines()[-10:]))
        print("\n--- LOG SERVIDOR (Últimas linhas) ---")
        print("\n".join(out_s.splitlines()[-10:]))

        if os.path.exists("test_client_temp.py"):
            os.remove("test_client_temp.py")

if __name__ == "__main__":
    run_verification()
