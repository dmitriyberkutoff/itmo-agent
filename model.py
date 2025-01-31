from dotenv import load_dotenv
from yandex_cloud_ml_sdk import YCloudML
import os
from utils.search import search

load_dotenv()

sdk = YCloudML(
    folder_id=os.getenv('YANDEX_FOLDER_ID'),
    auth=os.getenv('YANDEX_API_KEY'),
)


def get_answer(text: str) -> str:
    try:
        llm = sdk.models.completions("yandexgpt").configure(temperature=0)

        system_prompt = """Ты - агент, который отвечает на вопросы про университет ИТМО на основе данных источников. 
            Тебе на вход подается вопрос и источники, в которых нужно найти на него ответ. 
            Приоритет нужно отдавать официальным источникам ИТМО (itmo.ru, news.itmo.ru). 
            В вопросе могут быть варианты ответа (их порядок не важен), а могут не быть.

            Формат запроса:
            - Вопрос
            - Опционально варианты ответов от 1 до 10, разделены переносом строки
            - Источники информации

            Формат ответа:
            - Верни JSON с тремя полями: 
            - `answer` (число): 
                - номер правильного варианта от 1 до 10, если они были в вопросе
                - 0, если варианты не предложены или вопрос не предполагает выбор из вариантов
            - `reasoning` (строка): подробное объяснение на русском языке, а последним предложением добавь, что информация получена с помощью YandexGPT
            - `sources` (список строк): список корректных url (начинаются с https://) источников, на которых нашел ответ

            Пример:
            {"answer": 1, "reasoning": "Главный корпус ИТМО находится..."}
            {"answer": 0, "reasoning": "ИТМО впервые вошел в список лучших университетов..."}
            """

        messages = [
            {
                "role": "system",
                "text": system_prompt
            },
            {
                "role": "user",
                "text": text,
            },
        ]
        result = llm.run(messages)
        result = result[0].text.replace('\n', ' ').strip('` ')
        return result
    except Exception as e:
        print(f"Error in answering: {str(e)}")
        return ""


def search_and_answer(query: str) -> str:
    texts = search(query)
    text = query + '\n\n'
    for url, urlText in texts.items():
        text += url + '\n' + urlText + '\n\n'

    res = get_answer(text)
    return res