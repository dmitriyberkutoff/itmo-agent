import os
from dotenv import load_dotenv
from yandex_cloud_ml_sdk import YCloudML
from utils.logger import log_info
from utils.search import search_scraper

load_dotenv()

sdk = YCloudML(
    folder_id=os.getenv('YANDEX_FOLDER_ID'),
    auth=os.getenv('YANDEX_API_KEY'),
)


async def get_answer(text: str) -> str:
    '''Answers the question with the provided sources'''
    await log_info("Getting answer")

    try:
        llm = sdk.models.completions("yandexgpt").configure(temperature=0)

        system_prompt = """
            Ты - агент, который отвечает на вопросы про университет ИТМО на основе данных источников. 
            Тебе на вход подается вопрос и источники, в которых нужно найти на него ответ и вывести его строго в формате JSON. 
            Приоритет нужно отдавать официальным источникам ИТМО (itmo.ru, news.itmo.ru). 
            В вопросе могут быть варианты ответа (их порядок не важен), а могут не быть.

            Формат запроса:
            - Вопрос
            - Опционально варианты ответов от 1 до 10, разделены переносом строки
            - Источники информации

            Структура ответа должна быть строго следующей:
            {
                "answer": (int) — если вопрос содержит номера вариантов ответа, укажи номер правильного варианта от 1 до 10; 
                если вариантов нет, укажи 0,
                "reasoning": (str) — подробно объясни на русском языке, почему выбранный ответ правильный, на основе источников, последним предложением добавь, что информация была получена с помощью YandexGPT
                "sources": (list) — список корректных url (начинаются с https://) источников, на которых нашел ответ
            }
            
            Правила:
            - Ответ должен быть валидным JSON, без лишних символов, пояснений или markdown-форматирования.
            
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

        await log_info('Request to LLM')

        result = llm.run(messages)

        if result is None or result[0] is None:
            await log_info('Result is empty')

        result = result[0].text.replace('\n', ' ').strip('` ')

        await log_info('LLM result: ' + result[:50])

        return result
    except Exception as e:
        print(f"Error in answering: {str(e)}")
        return ""


async def search_and_answer(query: str) -> str:
    '''Search information in the Internet for query, collects to one text and asks LLM'''
    url_text_map = await search_scraper.search(query)
    text_parts = [query]
    for url, text in url_text_map.items():
        text_parts.append(url + '\n' + text)

    llm_text = '\n\n'.join(text_parts)
    res = await get_answer(llm_text)
    return res
