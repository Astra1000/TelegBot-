import os
import configparser
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError

# Конфигурация
CONFIG_FILE = 'config.ini'
COMMANDS_DIR = 'commands'

# Загрузка конфигурации
config = configparser.ConfigParser()
if not os.path.exists(CONFIG_FILE):
    print("Введите данные из my.telegram.org")
    config['Telegram'] = {
        'api_id': input("API ID: "),
        'api_hash': input("API Hash: ")
    }
    with open(CONFIG_FILE, 'w') as f:
        config.write(f)
else:
    config.read(CONFIG_FILE)

api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']

# Инициализация клиента
client = TelegramClient(
    'userbot_session', 
    api_id, 
    api_hash,
    connection_retries=5  # Больше попыток подключения
)

# Загрузка команд
commands = {}
if os.path.exists(COMMANDS_DIR):
    for filename in os.listdir(COMMANDS_DIR):
        if filename.endswith('.py') and filename != '__init__.py':
            module_name = filename[:-3]
            try:
                module = __import__(f'{COMMANDS_DIR}.{module_name}', fromlist=['command'])
                commands[module.command] = module.handle_command
                print(f'Команда "{module.command}" загружена')
            except Exception as e:
                print(f'Ошибка загрузки {filename}: {str(e)}')
else:
    print(f"Папка {COMMANDS_DIR} не найдена, команды не загружены")

# Обработчик сообщений
@client.on(events.NewMessage)
async def message_handler(event):
    msg_text = event.raw_text
    prefixes = ['.l ', '.lp ', '.tlp ']
    
    for prefix in prefixes:
        if msg_text.startswith(prefix):
            cmd_text = msg_text[len(prefix):].strip()
            cmd_parts = cmd_text.split(maxsplit=1)
            command_name = cmd_parts[0]
            args = cmd_parts[1] if len(cmd_parts) > 1 else ''
            
            if command_name in commands:
                await commands[command_name](event, args)
            return

# Основная функция
async def main():
    try:
        await client.start()
        me = await client.get_me()
        print(f"Бот запущен как: {me.first_name} ({me.phone})")
        await client.run_until_disconnected()
    except SessionPasswordNeededError:
        # Исправленный ввод для Termux
        password = input('Введите пароль 2FA: ')
        await client.sign_in(password=password)
        await client.run_until_disconnected()
    except Exception as e:
        print(f"Критическая ошибка: {str(e)}")

if __name__ == '__main__':
    client.loop.run_until_complete(main())
