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
            
            После вопроса могут быть пронумерованные варианты ответа. 
            Если варианты есть, нужно выбрать из них тот, который наиболее точно подходит под ответ на вопрос.
            Номер варианта влияет на его правильность, тебе нужно выбрать тот номер, который соответствует найденному ответу.
            
            После выбора варианта ответа сравни его с остальными и убедись, что он соответствует вопросу и ответу. 
            
            Формат запроса:
            - Вопрос
            - Опционально варианты ответов от 1 до 10
            - Варианты разделены переносом строки
            - Источники информации

            Структура ответа должна быть строго следующей:
            {
                "answer": (int) — Важно: Если в вопросе есть варианты ответа (нумерованные 1, 2, 3, 4 и т.д.), ты должен выбрать номер варианта, который соответствует правильному значению. Если вариантов ответа нет, укажи 0,
                "reasoning": (str) — подробно объясни на русском языке, почему выбранный вариант ответ правильный, на основе источников,
                "sources": (list) — список корректных url (начинаются с https://) источников, на которых нашел ответ
            }
            
            Как выбрать ответ:
            - Найди правильный ответ в источниках.  
            - Определи номер варианта из списка, соответствующий этому ответу.  
            - В `answer` укажи только номер варианта, а в `reasoning` полное пояснение
            
            Правила:
            - Ответ должен быть валидным JSON, без лишних символов, пояснений или markdown-форматирования.
            
            Пример:
            {"answer": 2, "reasoning": "Главный корпус ИТМО находится..."}
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
    query = query.replace('\n', ' ')
    url_text_map = await search_scraper.search(query)
    text_parts = [query]
    for url, text in url_text_map.items():
        text_parts.append(url + '\n' + text)

    llm_text = '\n\n'.join(text_parts)
    res = await get_answer(llm_text)
    return res
