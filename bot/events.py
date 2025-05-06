import asyncio
import aiohttp
import re
from datetime import datetime
from typing import Dict, Any
from pathlib import Path
import json
from bot.config import Config
from bot.logger import log_data

# ========== CONFIGURAÇÕES ==========
DATA_DIR = Path("data")
EVENTOS_FILE = DATA_DIR / "eventos_notificados.json"
DATA_DIR.mkdir(exist_ok=True)

API_BASE_URL = f"https://api.sportmonks.com/v3/football/livescores/latest?api_token={Config.SPORTMONKS_API_KEY}&include=scores;participants;events&per_page=100"

PENALTY_ORDINAL_REGEX = re.compile(r'^\d+(st|nd|rd|th) Penalty$', re.IGNORECASE)

EVENTOS_CAPTURADOS = {
    "Penalty confirmed": "🛑 **Pênalti confirmado pelo VAR!**",
    "Foul": "🚨 **Falta na área! Pênalti possível!**",
    "Yellow Card": "⚠️ **Cartão na área! Pênalti em potencial!**",
    "Red Card": "🔴 **Cartão vermelho na área! Pode ser pênalti!**"
}
# ===================================

# ========== FUNÇÕES AUXILIARES ==========
def normalizar_chave(chave: str) -> str:
    """Padroniza a chave para comparação"""
    return chave.replace("Penalty", "Penalty").lower()

def carregar_eventos() -> set:
    """Carrega eventos já notificados do arquivo JSON"""
    try:
        with open(EVENTOS_FILE, 'r', encoding='utf-8') as f:
            return {normalizar_chave(chave) for chave in json.load(f)}
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

def salvar_eventos(eventos: set):
    """Salva os eventos notificados no arquivo JSON"""
    try:
        with open(EVENTOS_FILE, 'w', encoding='utf-8') as f:
            json.dump(list(eventos), f, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar eventos: {e}")

def formatar_tempo(evento: Dict[str, Any]) -> str:
    """Formata o tempo do evento incluindo acréscimos"""
    minuto = evento.get("minute", "?")
    extra = evento.get("extra_minute")
    tempo = f"{minuto}'"
    if extra:
        tempo += f"+{extra}'"
    return tempo

def criar_chave_evento(fixture_id: str, addition: str, tempo: str) -> str:
    """Cria uma chave única para o evento"""
    return normalizar_chave(f"{fixture_id}_{addition}_{tempo}")

def ocorreu_dentro_da_area(evento: Dict[str, Any]) -> bool:
    """
    Verifica se o evento ocorreu dentro da área baseado em:
    - meta.location (ex: "18 yds")
    - meta.zone (ex: "defensive")
    - description (ex: "inside box")
    """
    meta = evento.get("meta", {})
    location = str(meta.get("location", "")).lower()
    zone = str(meta.get("zone", "")).lower()
    descricao = str(evento.get("description", "")).lower()

    return (
        "18 yds" in location or
        "18-yard" in location or
        ("defensive" in zone and "box" in descricao) or
        ("attacking" in zone and "opposition box" in descricao)
    )

async def fetch_json(session: aiohttp.ClientSession, url: str, params=None):
    """Faz requisição HTTP e retorna JSON"""
    try:
        async with session.get(url, params=params, timeout=5) as response:
            if response.status == 200:
                return await response.json()
            print(f"Erro na API (HTTP {response.status})")
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        print(f"Falha na requisição: {type(e).__name__}: {str(e)}")
    return None
# =========================================

# ========== FUNÇÃO PRINCIPAL ==========
async def check_events(bot):
    """Monitora e notifica eventos de pênaltis em tempo real"""
    await bot.wait_until_ready()
    channel = bot.get_channel(Config.CHANNEL_ID)
    
    if not channel:
        print(f"Canal com ID {Config.CHANNEL_ID} não encontrado!")
        return

    eventos_notificados = carregar_eventos()

    async with aiohttp.ClientSession() as session:
        while not bot.is_closed():
            inicio_loop = datetime.now()
            try:
                print("\n" + "="*50)
                print("Iniciando nova verificação de eventos...")
                
                dados = await fetch_json(session, API_BASE_URL)
                if not dados or not isinstance(dados.get('data'), list):
                    print("Nenhum dado válido recebido da API")
                    await asyncio.sleep(5)
                    continue

                # Processa jogos ativos
                jogos_ativos = {}
                for jogo in dados['data']:
                    fixture_id = str(jogo.get('id'))
                    status = jogo.get('status')
                    
                    if status in ['FT', 'AOT', 'POST']:  # Ignora jogos finalizados
                        continue
                        
                    jogos_ativos[fixture_id] = {
                        'participants': jogo.get('participants', []),
                        'events': jogo.get('events', []),
                        'status': status
                    }

                eventos_processados = 0
                for fixture_id, jogo in jogos_ativos.items():
                    # Obtem nomes dos times
                    participants = jogo['participants']
                    home = next(
                        (t.get('name') for t in participants 
                         if isinstance(t, dict) and t.get('meta', {}).get('location') == 'home'),
                        "Desconhecido"
                    )
                    away = next(
                        (t.get('name') for t in participants 
                         if isinstance(t, dict) and t.get('meta', {}).get('location') == 'away'),
                        "Desconhecido"
                    )
                    
                    # Processa eventos do jogo
                    for evento in jogo['events']:
                        addition = str(evento.get('addition', '')).strip()
                        tipo = str(evento.get('type', '')).strip()
                        tempo = formatar_tempo(evento)
                        chave = criar_chave_evento(fixture_id, addition, tempo)

                        if chave in eventos_notificados:
                            continue

                        # 1. Eventos específicos de pênalti/VAR
                        if addition in EVENTOS_CAPTURADOS:
                            mensagem = (
                                f"🔔 **ALERTA DE PÊNALTI!**\n"
                                f"⚽ **{home} vs {away}**\n"
                                f"🕒 **Minuto:** {tempo}\n"
                                f"🚨 **Evento:** {EVENTOS_CAPTURADOS[addition]}\n"
                                f"\n||@here||"
                            )
                            await channel.send(mensagem)
                            eventos_notificados.add(chave)
                            eventos_processados += 1

                        # 2. Pênaltis ordinais (1st, 2nd, etc.)
                        elif PENALTY_ORDINAL_REGEX.match(addition):
                            mensagem = (
                                f"🔔 **ALERTA DE PÊNALTI!**\n"
                                f"⚽ **{home} vs {away}**\n"
                                f"🕒 **Minuto:** {tempo}\n"
                                f"🚨 **Evento:** {addition}\n"
                                f"\n||@here||"
                            )
                            await channel.send(mensagem)
                            eventos_notificados.add(chave)
                            eventos_processados += 1

                        # 3. Faltas/Cartões dentro da área
                        elif tipo in ["Foul", "Yellow Card", "Red Card"] and ocorreu_dentro_da_area(evento):
                            chave_area = criar_chave_evento(fixture_id, f"{tipo}_area", tempo)
                            if chave_area not in eventos_notificados:
                                mensagem = (
                                    f"🔔 **POSSÍVEL PÊNALTI!**\n"
                                    f"⚽ **{home} vs {away}**\n"
                                    f"🕒 **Minuto:** {tempo}\n"
                                    f"🚨 **Evento:** {EVENTOS_CAPTURADOS[tipo]}\n"
                                    f"📍 **Local:** {evento.get('meta', {}).get('location', 'N/A')}\n"
                                    f"\n||@here||"
                                )
                                await channel.send(mensagem)
                                eventos_notificados.add(chave_area)
                                eventos_processados += 1

                salvar_eventos(eventos_notificados)
                tempo_processamento = (datetime.now() - inicio_loop).total_seconds()
                print(f"Verificação completa. Eventos processados: {eventos_processados} | Tempo: {tempo_processamento:.2f}s")
                await asyncio.sleep(max(0, 6 - tempo_processamento))

            except Exception as e:
                print(f"ERRO CRÍTICO: {type(e).__name__}: {str(e)}")
                log_data["erros"].append({
                    "timestamp": datetime.now().isoformat(),
                    "erro": str(e),
                    "tipo": type(e).__name__,
                })
                await asyncio.sleep(5)
# ====================================