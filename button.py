from telebot import types

markup_menu = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
markup_menu.add(types.KeyboardButton("Количество токенов"))
markup_menu.add(types.KeyboardButton("Запустить GPT"))
markup_menu.add(types.KeyboardButton("SpechKit"))


markup_SpechKit = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
markup_SpechKit.add(types.KeyboardButton("/stt"))
markup_SpechKit.add(types.KeyboardButton("/tts"))

markup_GPT = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
markup_GPT.add(types.KeyboardButton("Текстовый запрос"))
markup_GPT.add(types.KeyboardButton("Голосовой запрос"))

