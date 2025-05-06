from bot.config import setup_bot, Config
from bot.logger import configure_logging
from bot.events import check_events

def main():
    configure_logging()
    bot = setup_bot()
    
    @bot.event
    async def on_ready():
        print(f"Bot conectado como {bot.user}")
        bot.loop.create_task(check_events(bot))
    
    try:
        bot.run(Config.DISCORD_TOKEN)
    except Exception as e:
        print(f"Erro ao iniciar bot: {e}")

if __name__ == "__main__":
    main()