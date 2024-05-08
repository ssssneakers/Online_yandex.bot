token = '6922861550:AAG6-PugcPBe68GTOQ3TcvgJtHlI9_rtLc0'
iam_token = "t1.9euelZqUipCYyZfJlMmZiZSemI6UjO3rnpWay4qRyMiRipKTz5PMzJCRipvl9PcdVxZO-e8OJ2CY3fT3XQUUTvnvDidgmM3n9euelZqZnouYk4uSyZeLy4_Kk5Kble_8xeuelZqZnouYk4uSyZeLy4_Kk5Kblb3rnpWay5WOy8uXxsqbm8edjsaKlIm13oac0ZyQko-Ki5rRi5nSnJCSj4qLmtKSmouem56LntKMng.WJcoRkwlWftop5RdS5gjUkiyTgLqpvzs7zuvaADNSZ45w9JBJmY1S4OkzigRLyB2Zbb5erbx3YAmhAWO3QjhDQ"
folder_id = 'b1gi3skn9nv4g8ggcto3'
# путь к папке с проектом

MAX_USERS = 3  # максимальное кол-во пользователей
MAX_GPT_TOKENS = 120  # максимальное кол-во токенов в ответе GPT
COUNT_LAST_MSG = 4  # кол-во последних сообщений из диалога

# лимиты для пользователя
MAX_USER_STT_BLOCKS = 5  # 10 аудиоблоков
MAX_USER_TTS_SYMBOLS = 100  # 5 000 символов
MAX_USER_GPT_TOKENS = 2000  # 2 000 токенов

 # файл для базы данных
SYSTEM_PROMPT = 'Ты веселый собеседник.Давай наиболее понятный и самый краткий ответ' # список с системным промтом

HOME_DIR = '/home/student/Online_yandex.bot'  # путь к папке с проектом
LOGS = f'{HOME_DIR}/logs.txt'  # файл для логов
DB_FILE = f'{HOME_DIR}/messages.db'  # файл для базы данных

IAM_TOKEN_PATH = f'{HOME_DIR}/creds/iam_token.txt'  # файл для хранения iam_token
FOLDER_ID_PATH = f'{HOME_DIR}/creds/folder_id.txt'  # файл для хранения folder_id
BOT_TOKEN_PATH = f'{HOME_DIR}/creds/bot_token.txt'  # файл для хранения bot_token