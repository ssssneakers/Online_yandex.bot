import sqlite3
import logging  # модуль для сбора логов
# подтягиваем константы из config-файла
from config import LOGS, DB_FILE, MAX_USER_GPT_TOKENS, MAX_USER_TTS_SYMBOLS, MAX_USER_STT_BLOCKS

# настраиваем запись логов в файл
logging.basicConfig(filename=LOGS, level=logging.ERROR,
                    format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")
path_to_db = DB_FILE  # файл базы данных


# создаём базу данных и таблицу messages
def create_database():
    try:
        # подключаемся к базе данных
        with sqlite3.connect(path_to_db) as conn:
            cursor = conn.cursor()
            # создаём таблицу messages
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                user_id INTEGER PRIMARY KEY,
                txt TEXT,
                total_gpt_tokens INTEGER,
                tts_symbols INTEGER,
                stt_blocks INTEGER)
            ''')
            logging.info("DATABASE: База данных создана")  # делаем запись в логах
    except Exception as e:
        logging.error(e)  # если ошибка - записываем её в логи
        return None


def add_message(user_id):
    try:
        # подключаемся к базе данных
        with sqlite3.connect(path_to_db) as conn:
            cursor = conn.cursor()
            # записываем в таблицу новое сообщение
            cursor.execute('''
                    INSERT INTO messages (user_id, txt, total_gpt_tokens, tts_symbols, stt_blocks) 
                    VALUES (?, ?, ?, ?, ?)''',
                           (user_id, '', MAX_USER_GPT_TOKENS, MAX_USER_TTS_SYMBOLS, MAX_USER_STT_BLOCKS)
                           )
            conn.commit()  # сохраняем изменения
            logging.info(f"DATABASE: INSERT INTO messages "
                         f"well done!")
    except Exception as e:
        logging.error(e)  # если ошибка - записываем её в логи
        return None

def check_user():
    try:
        # подключаемся к базе данных
        with sqlite3.connect(path_to_db) as conn:
            cursor = conn.cursor()
            # получаем количество уникальных пользователей помимо самого пользователя
            cursor.execute('''SELECT COUNT(DISTINCT user_id) FROM messages''')
            count = cursor.fetchone()
            return count[0]
    except Exception as e:
        logging.error(e)  # если ошибка - записываем её в логи
        return None


def select_function(user_id):
    try:
        # подключаемся к базе данных
        with sqlite3.connect(path_to_db) as conn:
            cursor = conn.cursor()
            # получаем количество уникальных пользователей помимо самого пользователя
            cursor.execute('''SELECT user_id FROM messages WHERE user_id = ?''', user_id)
            count = cursor.fetchone()
            return count is not None
    except Exception as e:
        logging.error(e)  # если ошибка - записываем её в логи
        return None

def count_token(user_id):
    try:
        with sqlite3.connect(path_to_db) as conn:
            cursor = conn.cursor()
            # Проверяем, существует ли запись для данного user_id
            cursor.execute('SELECT * FROM messages WHERE user_id = ?', (user_id,))
            record = cursor.fetchone()
            if record is None:
                # Если записи нет, то создаем ее с начальными значениями
                add_message(user_id)
                return '', MAX_USER_GPT_TOKENS, MAX_USER_TTS_SYMBOLS, MAX_USER_STT_BLOCKS
            else:
                # Если запись существует, возвращаем ее данные
                return record[1], record[2], record[3], record[4]
    except Exception as e:
        logging.error(e)
        return None


def update_tokens(user_id, total_gpt_tokens, tts_symbols, stt_blocks, txt):
    try:
        with sqlite3.connect(path_to_db) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE messages
                SET total_gpt_tokens = ?, tts_symbols = ?, stt_blocks = ?, txt = ?
                WHERE user_id = ?
            ''', (total_gpt_tokens, tts_symbols, stt_blocks, txt, user_id))
            conn.commit()
            logging.info(f"DATABASE: Токены пользователя {user_id} обновлены")
    except Exception as e:
        logging.error(e)

