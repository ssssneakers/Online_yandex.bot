import telebot
from config import LOGS
from button import markup_menu, markup_SpechKit, markup_GPT
from Gpt import ask_gpt
from database import create_database, add_message, count_token, update_tokens, check_user, select_function
from SpechKit import speech_to_text, speech_to_voice
import logging
import math
from creds import get_bot_token

token = get_bot_token()
bot = telebot.TeleBot(token)

logging.basicConfig(filename=LOGS, level=logging.ERROR, format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")

@bot.message_handler(commands=['start'])
def start(message):
    try:
        user_id = message.from_user.id
        user_li = check_user()
        database = create_database()
        if not database:
            create_database()
            add_message(user_id)
        if user_li < 2:
            if not select_function((user_id,)):
                add_message(user_id)
                bot.send_message(message.chat.id, 'Привет! Если хочешь узнать функции бота, введи команду /help', reply_markup=markup_menu)
            else:
                bot.send_message(message.chat.id, 'Здороу! Если хочешь вспомнить функции бота, введи команду /help', reply_markup=markup_menu)
        else:
            # Проверяем, зарегистрирован ли уже пользователь
            if select_function((user_id,)):
                bot.send_message(message.chat.id, 'Здороу! Если хочешь вспомнить функции бота, введи команду /help', reply_markup=markup_menu)
            else:
                bot.send_message(message.chat.id, 'Лимит пользователей исчерпан. Попробуйте позже')
    except:
        bot.register_next_step_handler(message, start)


    # Здесь можете добавить дополнительные команды или сообщения, если это необходимо


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, 'Этот бот позволяет пользователю общаться с нейросетью при помощи голоса!\n'
                                      'Если хочешь проверить хорошо ли распознается твой голос без запросов к нейросети, нажми на кнопку "SpechKit и выбери нужную функцию \n"'
                                      'Команда /tts позволяет преобразовать текст в голосовое сообщение \n'
                                      'Команда /stt позволяет преобразовать голос в текст \n'
                                      'А если хочешь задать вопрос нейросети используй кнопку "Запустить GPT" и задай вопрос либо текстом либо голосом\n'
                                      'Если хочешь задать вопрос нейросети используй кнопку "Текстовый запрос"\n'
                                      'Если хочешь задать вопрос голосом нейросети используй кнопку "Голосовой запрос"\n'
                                      'Помни о лимитах!', reply_markup=markup_menu)


@bot.message_handler(func=lambda message: message.text == 'SpechKit')
def spechkit(message):
    bot.send_message(message.chat.id, 'Выбери что тебе нужно', reply_markup=markup_SpechKit)
    token = count_token(message.from_user.id)
    _, total_gpt_tokens, tts_symbols, stt_blocks = token
    if 0 >= tts_symbols:
        bot.send_message(message.chat.id, 'Вы превысили лимит символов для создания голосовых сообщений.Создание голосовых сообщений невозможно')
    if 0 >= stt_blocks:
        bot.send_message(message.chat.id, 'Вы превысили лимит блоков для распознавания голоса.Распознавание голоса невозможно')


@bot.message_handler(commands=['stt'])
def stt(message):
    user_id = message.from_user.id
    token = count_token(user_id)
    _, total_gpt_tokens, tts_symbols, stt_blocks = token
    if 0 >= stt_blocks:
        bot.send_message(user_id, 'Ваш лимит токенов истек. Попробуй снова', reply_markup=markup_menu)
    else:
        bot.send_message(message.chat.id, 'Отправь голосовое сообщение')
        bot.register_next_step_handler(message, stt1)


def stt1(message):
    try:
        user_id = message.from_user.id
        token = count_token(user_id)
        txt, total_gpt_tokens, tts_symbols, stt_blocks = token

        # Проверка, что сообщение действительно голосовое
        if not message.voice:
            bot.send_message(user_id, 'Пожалуйста, отправьте голосовое сообщение!')
            bot.register_next_step_handler(message, stt)

        duration = message.voice.duration  # получаем длительность голосового сообщения
        Token = math.ceil(duration / 15)

        if duration >= 30:
            msg = "SpeechKit STT работает с голосовыми сообщениями меньше 30 секунд"
            bot.send_message(user_id, msg)
            return None

        if Token > stt_blocks:
            bot.send_message(user_id, f'Превышен лимит токенов. Использовано {Token} токенов. Доступно: {stt_blocks}')
            bot.register_next_step_handler(message, stt)
            return

        file_id = message.voice.file_id  # получаем id голосового сообщения
        file_info = bot.get_file(file_id)  # получаем информацию о голосовом сообщении
        file = bot.download_file(file_info.file_path)

        # распознаем голосовое сообщение
        status, text = speech_to_text(file)

        if status:
            txt += text
            stt_blocks -= Token
            update_tokens(user_id, total_gpt_tokens, tts_symbols, stt_blocks, txt)
            bot.send_message(user_id, f'Текст: {text}')
        else:
            bot.send_message(user_id, f'Произошла ошибка при распознавании голосового сообщения: {text}')

    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {e}")


@bot.message_handler(commands=['tts'])
def tts(message):
    user_id = message.from_user.id
    token = count_token(user_id)
    _, total_gpt_tokens, tts_symbols, stt_blocks = token
    if 0 >= tts_symbols:
        bot.send_message(user_id, 'Ваш лимит токенов истек. Попробуй снова', reply_markup=markup_menu)
    else:
        bot.send_message(message.chat.id, 'Напишите текст для преобразования в голосовое сообщение')
        bot.register_next_step_handler(message, tts1)


def tts1(message):
    try:
        text = message.text
        success, response = speech_to_voice(text)
        text_symbols = len(text)
        user_id = message.from_user.id
        token = count_token(user_id)
        txt, total_gpt_tokens, tts_symbols, stt_blocks = token

        if message.content_type != 'text':
            bot.send_message(user_id, 'Отправь текстовое сообщение')
            return
        if text_symbols > tts_symbols:
            bot.send_message(user_id, 'Текст слишком большой. Попробуй снова')
            bot.register_next_step_handler(message, tts)
        if success:
            txt += text
            tts_symbols -= text_symbols
            update_tokens(user_id, total_gpt_tokens, tts_symbols, stt_blocks, txt)
            bot.send_voice(message.chat.id, response, reply_markup=markup_menu)
        else:
            bot.send_message(message.chat.id, f"Ошибка: {response}", reply_markup=markup_menu)
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {e}")
        bot.register_next_step_handler(message, start)


@bot.message_handler(func=lambda message: message.text == 'Запустить GPT')
def gpt(message):
    try:
        user_id = message.from_user.id
        token = count_token(user_id)
        if token is None:
            bot.send_message(user_id, 'Ошибка: информация о токенах не найдена', reply_markup=markup_menu)
            return
        _, total_gpt_tokens, tts_symbols, stt_blocks = token
        if total_gpt_tokens <= 0:
            bot.send_message(user_id, 'Ваш лимит токенов истек', reply_markup=markup_menu)
        else:
            bot.send_message(message.chat.id, 'Выберете какую функцию хочешь запустить', reply_markup=markup_GPT)
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {e}", reply_markup=markup_menu)


@bot.message_handler(func=lambda message: message.text == 'Голосовой запрос')
def gpt_voice_handler(message):
    try:
        user_id = message.from_user.id
        token = count_token(user_id)
        _, total_gpt_tokens, tts_symbols, stt_blocks = token
        if total_gpt_tokens <= 0:
            bot.send_message(user_id, 'Ваш лимит токенов истек', reply_markup=markup_menu)
            return

        if 0 >= stt_blocks:
            bot.send_message(user_id, 'Ваш лимит токенов истек. Попробуй снова', reply_markup=markup_menu)
            return

        bot.send_message(message.chat.id, 'Отправь голосовое сообщение')
        bot.register_next_step_handler(message, gpt_voice)
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {e}", reply_markup=markup_menu)


def gpt_voice(message):
    try:
        user_id = message.from_user.id
        token = count_token(user_id)
        txt, total_gpt_tokens, tts_symbols, stt_blocks = token

        # Проверка, что сообщение действительно голосовое
        if not message.voice:
            bot.send_message(user_id, 'Пожалуйста, отправьте голосовое сообщение!')
            bot.register_next_step_handler(message, stt)

        duration = message.voice.duration  # получаем длительность голосового сообщения
        Token = math.ceil(duration / 15)

        if duration >= 30:
            msg = "SpeechKit STT работает с голосовыми сообщениями меньше 30 секунд"
            bot.send_message(user_id, msg)
            return None

        if Token > stt_blocks:
            bot.send_message(user_id, f'Превышен лимит токенов. Использовано {Token} токенов. Доступно: {stt_blocks}')
            bot.register_next_step_handler(message, gpt_voice_handler)
            return

        file_id = message.voice.file_id  # получаем id голосового сообщения
        file_info = bot.get_file(file_id)  # получаем информацию о голосовом сообщении
        file = bot.download_file(file_info.file_path)

        # распознаем голосовое сообщение
        status, text = speech_to_text(file)

        if status:
            txt += text
            stt_blocks -= Token
            total_gpt_tokens -= len(text)
            update_tokens(user_id, total_gpt_tokens, tts_symbols, stt_blocks, txt)
            try:
                Gpt_text = ask_gpt(text)
                txt += Gpt_text
                success, response = speech_to_voice(Gpt_text)
                if success:
                    bot.send_voice(user_id, response, reply_markup=markup_menu)
                else:
                    bot.send_message(message.chat.id, f"Ошибка: {response}", reply_markup=markup_menu)
            except Exception as e:
                bot.send_message(user_id, f'Произошла ошибка SpechKit: {e}', reply_markup=markup_menu)

        else:
            bot.send_message(user_id, f'Произошла ошибка при распознавании голосового сообщения: {text}', reply_markup=markup_menu)

    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {e}", reply_markup=markup_menu)


@bot.message_handler(func=lambda message: message.text == 'Текстовый запрос')
def gpt_handler(message):
    bot.send_message(message.chat.id, 'Отправь текстовое сообщение')
    bot.register_next_step_handler(message, gpt_text)


def gpt_text(message):
    try:
        text = message.text
        if message.content_type != 'text':
            bot.send_message(message.chat.id, 'Неправильный формат. Отправь текстовое сообщение')
            return
        user_id = message.from_user.id
        token = count_token(user_id)
        txt, total_gpt_tokens, tts_symbols, stt_blocks = token
        txt += text
        if total_gpt_tokens <= 0:
            bot.send_message(user_id, 'Ваш лимит токенов истек', reply_markup=markup_menu)
        else:
            try:
                result = ask_gpt(text)
                txt += result
                total_gpt_tokens -= len(text)
                update_tokens(user_id, total_gpt_tokens, tts_symbols, stt_blocks, txt)
                bot.send_message(message.chat.id, f'{result}', reply_markup=markup_menu)
            except Exception as e:
                bot.send_message(message.chat.id, f"Произошла ошибка при запросе к Gpt: {e}", reply_markup=markup_menu)
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {e}", reply_markup=markup_menu)


@bot.message_handler(func=lambda message: message.text == 'Количество токенов')
def user_token(message):
    user_id = message.from_user.id
    token = count_token(user_id)
    txt, total_gpt_tokens, tts_symbols, stt_blocks = token
    bot.send_message(user_id, f'Ваш лимит токенов для нейросети: {total_gpt_tokens}')
    bot.send_message(user_id, f'Ваш лимит символов для создания голосовых сообщений: {tts_symbols}')
    bot.send_message(user_id, f'Ваш лимит блоков для распознавания голоса: {stt_blocks}', reply_markup=markup_menu)


@bot.message_handler(commands=['debug'])
def debug(message):
    with open("logs.txt", "rb") as f:
        bot.send_document(message.chat.id, f)


bot.polling()
