# Projeto Mini-NET

## Descrição

Implementação de uma pilha completa de protocolos de rede construída sobre UDP, simulando as camadas de Enlace (Link), Rede (Network) e Transporte (Transport) do modelo TCP/IP. O projeto demonstra como construir um sistema de comunicação confiável sobre um canal não confiável que simula perda de pacotes e corrupção de dados.

## Objetivo

Desmistificar o funcionamento da Internet implementando manualmente:
- **Camada de Aplicação**: Chat com formato JSON
- **Camada de Transporte**: Protocolo Stop-and-Wait para confiabilidade
- **Camada de Rede**: Roteamento com endereçamento virtual (VIP) e TTL
- **Camada de Enlace**: Verificação de integridade com CRC32

## Arquitetura do Sistema

```
Cliente (127.0.0.1:8080)
    ↓
Roteador (127.0.0.1:6000)  ← Canal com Ruído (20% perda, 20% corrupção)
    ↓
Servidor (127.0.0.1:9090)
```

### Encapsulamento (Bonecas Russas)
```
Quadro [MAC_SRC, MAC_DST, FCS/CRC32]
  └─ Pacote [VIP_SRC, VIP_DST, TTL]
      └─ Segmento [SEQ, ACK, Payload]
          └─ JSON [sender, message, timestamp]
```

## Requisitos

- **Python 3.8+**
- **Bibliotecas**: Apenas bibliotecas padrão (socket, json, time, zlib, random)

## Estrutura dos Arquivos

```
Projeto_Mini-NET/
│
├── protocol.py           # Biblioteca base (fornecida pelo professor)
│                         # Define Segmento, Pacote, Quadro e simulador de ruído
│
├── client.py             # Cliente do chat (Stop-and-Wait)
├── server.py             # Servidor do chat (recepção e ACKs)
├── router.py             # Roteador intermediário (Camada 3)
│
├── test_integration.py   # Script de teste automatizado
└── README.md             # Este arquivo
```

## Como Executar

### Passo 1: Abrir 3 Terminais

Você precisará de **3 terminais separados** para rodar os componentes do sistema.

### Passo 2: Iniciar o Roteador (Terminal 1)

```bash
cd Projeto_Mini-NET
python3 router.py
```

**Saída esperada:**
```
--- ROTEADOR INICIADO (127.0.0.1:6000) ---
```

### Passo 3: Iniciar o Servidor (Terminal 2)

```bash
cd Projeto_Mini-NET
python3 server.py
```

**Saída esperada:**
```
--- SERVIDOR INICIADO (127.0.0.1:9090) ---
--- VIP: SERVIDOR ---
```

### Passo 4: Iniciar o Cliente (Terminal 3)

```bash
cd Projeto_Mini-NET
python3 client.py
```

**Saída esperada:**
```
--- CLIENTE INICIADO (127.0.0.1:8080) ---
Digite sua mensagem e tecle ENTER para enviar.
[CLIENTE_A] >
```

### Passo 5: Enviar Mensagens

No Terminal 3 (Cliente), digite uma mensagem e pressione ENTER:

```
[CLIENTE_A] > Olá, servidor!
```

Observe os logs nos 3 terminais mostrando o tráfego passando pelas camadas.

## Fluxo de Comunicação

### Envio de Mensagem (Cliente → Servidor)

```
1. Cliente: Usuário digita "Olá"
2. Cliente: Cria Segmento(seq=0, payload={message: "Olá"})
3. Cliente: Encapsula em Pacote(src=CLIENTE_A, dst=SERVIDOR, ttl=5)
4. Cliente: Encapsula em Quadro(src=MAC_CLIENTE_A, dst=MAC_ROUTER)
5. Cliente: Calcula CRC32 e serializa em JSON
6. Cliente: Envia via enviar_pela_rede_ruidosa() → ROTEADOR

7. Roteador: Recebe e valida CRC
8. Roteador: Decrementa TTL (5 → 4)
9. Roteador: Consulta tabela: SERVIDOR → 127.0.0.1:9090
10. Roteador: Re-encapsula e envia → SERVIDOR

11. Servidor: Recebe e valida CRC
12. Servidor: Verifica dst_vip == SERVIDOR
13. Servidor: Extrai Segmento, verifica seq_num == expected_seq
14. Servidor: Exibe mensagem na APLICAÇÃO
15. Servidor: Cria ACK(seq=0) e envia de volta via ROTEADOR

16. Cliente: Recebe ACK, valida CRC e seq_num
17. Cliente: Alterna sequência (0 → 1)
18. Cliente: Pronto para próxima mensagem
```

## Tecnologias e Conceitos

- **UDP (User Datagram Protocol)**: Protocolo não confiável usado como base
- **Stop-and-Wait ARQ**: Protocolo de confiabilidade mais simples
- **CRC32**: Algoritmo de detecção de erros
- **Virtual IP (VIP)**: Endereçamento lógico da camada 3
- **TTL**: Mecanismo anti-loop em roteamento
- **Encapsulamento**: Princípio fundamental de redes em camadas

## Limitações Conhecidas

- Apenas 1 cliente suportado simultaneamente
- Roteamento estático

## Referências

- Kurose, J. F., & Ross, K. W. (2021). *Computer Networking: A Top-Down Approach*
- Tanenbaum, A. S. (2011). *Computer Networks*
- RFC 768 - User Datagram Protocol (UDP)
- RFC 791 - Internet Protocol (IP)

## Autores

Projeto desenvolvido para a disciplina de Redes de Computadores - 2025/4

**Curso**: Ciência da Computação

**Professor**: Hugo Marciano

**Alunos**:
- Rafael Machado Scafuto - 202103775
- Pedro de Melo Lobo Campos - 202200548
- João Gabriel Marques Pineli Chaveiro - 202200525

---

**Data de Entrega**: 26/02/2026

**Link do Repositório**: https://github.com/PedroCamps/redes

---

## Licença

Este projeto é educacional e foi desenvolvido como parte do Projeto Integrador da disciplina de Redes de Computadores.
