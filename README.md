# Bot de Monitoramento de Pênaltis no Futebol
Bot que monitora eventos de pênaltis, VAR e faltas/cartões na área **EM TEMPO REAL** usando a API da SportMonks e notifica em um canal do Discord.

# ❓ **O que o bot detecta?**
+ Pênaltis confirmados pelo VAR
+ Faltas e cartões dentro da área
+ Penalidades ordinais (ex: 1st Penalty)

# 🧠 Observações
+ O bot salva eventos já notificados para evitar repetição.
+ Sistema de LOGS completo.

## 🛠 Tecnologias utilizadas

- [Python-3.9+](https://www.python.org/downloads/)
- [discord.py](https://discordpy.readthedocs.io/)
- [aiohttp](https://docs.aiohttp.org/)
- [python-dotenv](https://github.com/theskumar/python-dotenv)
- [SportMonks Football API](https://sportmonks.com)



## 🚀 Como executar

1. **Clone o projeto**:
   ```bash
   git clone https://github.com/ravivver/Bot-Discord-PENAL.git
   cd bot-penaltis

2. **Crie e ative um ambiente virtual (recomendado):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    venv\Scripts\activate  # Windows

3. **Crie e edite seu arquivo .env**:
    ```env
    DISCORD_TOKEN=seu_token_discord
    SPORTMONKS_API_KEY=sua_api_key
    CHANNEL_ID=id_do_canal

4. **Instale as Dependências**:
    ```bash
    pip install -r requirements.txt
   
5. **Execute o Bot**:
    ```bash
    python main.py

# Configuração

Você pode ajustar:

+ O intervalo de verificação modificando o await asyncio.sleep() em events.py
+ Os tipos de eventos monitorados editando o dicionário EVENTOS_CAPTURADOS
+ O formato das mensagens nas funções de criação de mensagem

# Estrutura de Arquivos
+ main.py - Ponto de entrada do bot
+ bot/ - Módulo principal
    + config.py - Configurações e setup
    + events.py - Lógica de monitoramento de eventos
    + logger.py - Configuração de logs
+ .env - Variáveis de ambiente
+ requirements.txt - Dependências

# Sobre Dependências
Verifique o arquivo requirements.txt para todas as dependências necessárias...
