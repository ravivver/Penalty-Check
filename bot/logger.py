import logging
import json
from pathlib import Path
import sys
from datetime import datetime

LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "bot_logs.json"
LOG_DIR.mkdir(exist_ok=True)

log_data = {
    "avisos_enviados": [],
    "erros": [],
    "eventos": []
}

def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(LOG_DIR / "bot_console.log", encoding='utf-8')
        ]
    )

def salvar_logs():
    try:
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
        logging.info("Logs salvos com sucesso!")
    except Exception as e:
        logging.error(f"Erro ao salvar logs: {e}")