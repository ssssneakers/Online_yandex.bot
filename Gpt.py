import requests
import logging  # модуль для сбора логов
from config import MAX_GPT_TOKENS, SYSTEM_PROMPT, LOGS
from creds import get_creds  # модуль для получения токенов

iam_token, folder_id = get_creds()
# настраиваем запись логов в файл
logging.basicConfig(filename=LOGS, level=logging.ERROR, format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")


# подсчитываем количество токенов в сообщениях
def count_gpt_tokens(messages):
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/tokenizeCompletion"
    headers = {
        'Authorization': f'Bearer {iam_token}',
        'Content-Type': 'application/json'
    }
    data = {
        'modelUri': f"gpt://{folder_id}/yandexgpt-lite",
        "messages": messages
    }
    try:
        return len(requests.post(url=url, json=data, headers=headers).json()['tokens'])
    except Exception as e:
        logging.error(e)  # если ошибка - записываем её в логи
        return 0


# запрос к GPT
def ask_gpt(text):  # Название функции может быть другое
    headers = {
        'Authorization': f'Bearer {iam_token}',
        'Content-Type': 'application/json'
    }
    data = {
        "modelUri": f"gpt://{folder_id}/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.8,
            "maxTokens": MAX_GPT_TOKENS
        },
        "messages": [
            {
                "role": "system",
                "text": SYSTEM_PROMPT  # Сюда прописать свой системный промт или же вставить переменную с системным промтом
            },
            {
                "role": "user",
                "text": text
            }
        ]
    }
    response = requests.post("https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
                             headers=headers,
                             json=data)
    if response.status_code == 200:
        text = response.json()["result"]["alternatives"][0]["message"]["text"]
        print(response.json()["result"])
        return text
    else:
        return 'Ошибка'
