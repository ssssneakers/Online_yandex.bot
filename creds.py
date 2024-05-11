import json
import logging
import time
from datetime import datetime
import requests
from config import LOGS, IAM_TOKEN_PATH, FOLDER_ID_PATH, BOT_TOKEN_PATH

logging.basicConfig(filename=LOGS, level=logging.INFO,
                    format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")


def get_bot_token():
    with open(BOT_TOKEN_PATH, 'r') as f:
        file_data = json.load(f)
        token = file_data["bot_token"]
        return token


def get_creds():
    try:
        with open(IAM_TOKEN_PATH, 'r') as f:
            file_data = json.load(f)
            expiration = datetime.strptime(file_data["expires_at"][:26], '%Y-%m-%dT%H:%M:%S.%f')
            if expiration < datetime.now():
                create_new_token()
    except:
        create_new_token()

    with open(IAM_TOKEN_PATH, 'r') as f:
        file_data = json.load(f)
        aim_token = file_data["access_token"]

    with open(FOLDER_ID_PATH, 'r') as f:
        file_d = json.load(f)
        folder_id = file_d["folder_id"]

    return aim_token, folder_id


def create_new_token():
    url = "http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token"
    headers = {
        "Metadata-Flavor": "Google"
    }
    try:
        response = requests.get(url=url, headers=headers)
        if response.status_code == 200:
            token_data = response.json()  # вытаскиваем из ответа iam_token
            # добавляем время истечения iam_token к текущему времени
            token_data['expires_at'] = time.time() + token_data['expires_in']
            # записываем iam_token в файл
            with open(IAM_TOKEN_PATH, "w") as token_file:
                json.dump(token_data, token_file)
            logging.info("Получен новый iam_token")
        else:
            logging.error(f"Ошибка получения iam_token. Статус-код: {response.status_code}")
    except Exception as e:
        logging.error(f"Ошибка получения iam_token: {e}")
