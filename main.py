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
client = TelegramClient('userbot_session', api_id, api_hash)

# Загрузка команд
commands = {}
for filename in os.listdir(COMMANDS_DIR):
    if filename.endswith('.py') and filename != '__init__.py':
        module_name = filename[:-3]
        try:
            module = __import__(f'{COMMANDS_DIR}.{module_name}', fromlist=['command'])
            commands[module.command] = module.handle_command
            print(f'Команда "{module.command}" загружена')
        except ImportError as e:
            print(f'Ошибка загрузки {filename}: {str(e)}')

# Обработчик сообщений
@client.on(events.NewMessage)
async def message_handler(event):
    msg_text = event.raw_text
    prefixes = ['.l ', '.lp ', '.tlp ']  # Пробел после префикса важен!
    
    if any(msg_text.startswith(prefix) for prefix in prefixes):
        for prefix in prefixes:
            if msg_text.startswith(prefix):
                cmd_text = msg_text[len(prefix):].strip()
                break
        
        cmd_parts = cmd_text.split(maxsplit=1)
        command_name = cmd_parts[0]
        args = cmd_parts[1] if len(cmd_parts) > 1 else ''
        
        if command_name in commands:
            await commands[command_name](event, args)

# Основная функция
async def main():
    try:
        await client.start()
        me = await client.get_me()
        print(f"Бот запущен как: {me.first_name} ({me.phone})")
        await client.run_until_disconnected()
    except SessionPasswordNeededError:
        await client.sign_in(password=input('Введите пароль: '))

if __name__ == '__main__':
    client.loop.run_until_complete(main())
