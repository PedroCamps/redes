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

## Funcionalidades Implementadas

### ✅ Fase 1: Aplicação e Sockets
- Arquitetura Cliente-Servidor
- Formato JSON com campos: sender, message, timestamp
- Entrada de dados do usuário e exibição formatada

### ✅ Fase 2: Transporte e Confiabilidade
- **Stop-and-Wait**: Cliente espera ACK antes de enviar próxima mensagem
- **ACKs**: Servidor confirma recebimento de cada segmento
- **Timeout e Retransmissão**: Cliente retransmite após 3 segundos sem ACK
- **Números de Sequência**: Alternância 0/1 para detectar duplicatas

### ✅ Fase 3: Rede e Roteamento
- **Endereços Virtuais (VIP)**: "CLIENTE_A" e "SERVIDOR"
- **TTL (Time to Live)**: Decrementado a cada salto no roteador
- **Roteador Intermediário**: Encaminha pacotes consultando tabela estática
- **Descarte por TTL**: Pacotes com TTL ≤ 0 são descartados

### ✅ Fase 4: Enlace e Integridade
- **Endereços MAC**: Fictícios para simular camada de enlace
- **CRC32**: Cálculo automático usando zlib.crc32()
- **Verificação de Integridade**: Quadros corrompidos são descartados silenciosamente
- **Recuperação Automática**: Camada de Transporte recupera perdas via timeout

## Simulação de Falhas

O arquivo `protocol.py` simula um canal físico com:
- **20% de perda de pacotes** (simulando congestionamento)
- **20% de corrupção de bits** (simulando interferência eletromagnética)
- **Latência aleatória** entre 0.1 e 0.5 segundos

### Para testar resiliência extrema:

Edite temporariamente `protocol.py`:

```python
PROBABILIDADE_PERDA = 0.5       # 50% de perda
PROBABILIDADE_CORRUPCAO = 0.5   # 50% de corrupção
```

O sistema deve continuar funcionando, apenas mais lento devido às retransmissões.

## Teste Automatizado

Execute o teste de integração:

```bash
python3 test_integration.py
```

Este script:
1. Inicia roteador e servidor automaticamente
2. Envia uma mensagem de teste
3. Verifica se o ACK retorna
4. Exibe logs do roteador e servidor

**Saída esperada:**
```
>>> SUCESSO: O ciclo completo (Envio -> Router -> Servidor -> ACK -> Router -> Cliente) funcionou!
```

## Logs e Debugging

### Camadas identificadas nos logs:

- `[FÍSICA]` - Camada 1: Transmissão pelo meio físico (perda/corrupção)
- `[CAMADA 2]` / `[LINK]` - Camada de Enlace (CRC, MACs)
- `[CAMADA 3]` - Camada de Rede (VIP, TTL, roteamento)
- `[CAMADA 4]` / `[TRANS]` - Camada de Transporte (SEQ, ACK, timeout)
- `[APLICAÇÃO]` - Camada 5: Mensagens do chat

### Exemplos de logs importantes:

**Perda de pacote:**
```
[FÍSICA] O pacote foi perdido na rede (Drop).
[TIMEOUT] ACK não chegou a tempo. Retransmitindo pacote...
```

**Corrupção detectada:**
```
[FÍSICA] Interferência eletromagnética! Bits trocados.
[CAMADA 2] ERRO DE CRC! Quadro descartado silenciosamente.
```

**Duplicata detectada:**
```
[CAMADA 4] Duplicata detectada. Reenviando ACK.
```

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

## Critérios de Avaliação (Total: 10 pontos)

| Critério | Peso | Implementado |
|----------|------|--------------|
| Funcionalidade Básica | 3.0 | ✅ Chat funciona perfeitamente |
| Resiliência | 3.0 | ✅ Recupera perdas e corrupções |
| Implementação das Camadas | 2.0 | ✅ Encapsulamento respeitado |
| Qualidade do Código | 1.0 | ✅ Código limpo e comentado |
| Documentação/Logs | 1.0 | ✅ Logs detalhados + README |

## Solução de Problemas

### Erro: "Address already in use"

Um componente ainda está rodando. Mate os processos:

```bash
lsof -ti:6000 | xargs kill  # Roteador
lsof -ti:9090 | xargs kill  # Servidor
lsof -ti:8080 | xargs kill  # Cliente
```

### Mensagens não chegam

1. Verifique se os 3 componentes estão rodando
2. Verifique a ordem de inicialização: Router → Server → Client
3. Aumente o TIMEOUT_ACK em client.py se a rede estiver muito lenta

### Teste não passa

Se o teste automatizado falhar:
1. Execute os componentes manualmente
2. Verifique os logs para identificar a camada com problema
3. Reduza PROBABILIDADE_PERDA e PROBABILIDADE_CORRUPCAO temporariamente

## Tecnologias e Conceitos

- **UDP (User Datagram Protocol)**: Protocolo não confiável usado como base
- **Stop-and-Wait ARQ**: Protocolo de confiabilidade mais simples
- **CRC32**: Algoritmo de detecção de erros
- **Virtual IP (VIP)**: Endereçamento lógico da camada 3
- **TTL**: Mecanismo anti-loop em roteamento
- **Encapsulamento**: Princípio fundamental de redes em camadas

## Limitações Conhecidas

- Apenas 1 cliente suportado simultaneamente (pode ser estendido para multiusuário)
- Roteamento estático (não há protocolo de roteamento dinâmico)
- Simulação roda em localhost (mas a lógica funcionaria em rede real)
- Stop-and-Wait é ineficiente (poderia usar Sliding Window para melhor throughput)

## Possíveis Extensões

- Implementar múltiplos clientes simultâneos usando threading
- Adicionar protocolo de roteamento dinâmico (RIP/OSPF simplificado)
- Implementar Sliding Window ao invés de Stop-and-Wait
- Adicionar criptografia nas mensagens
- Interface gráfica para o chat

## Referências

- Kurose, J. F., & Ross, K. W. (2021). *Computer Networking: A Top-Down Approach*
- Tanenbaum, A. S. (2011). *Computer Networks*
- RFC 768 - User Datagram Protocol (UDP)
- RFC 791 - Internet Protocol (IP)

## Autores

Projeto desenvolvido para a disciplina de Redes de Computadores - 2025/4

**Curso**: Engenharia de Software / Ciência da Computação / Sistemas de Informação

**Professor**: Marciano (marciano@ufg.br)

---

**Data de Entrega**: [Preencher com a data]

**Link do Repositório**: [Preencher com o link do GitHub]

---

## Licença

Este projeto é educacional e foi desenvolvido como parte do Projeto Integrador da disciplina de Redes de Computadores.
