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
    """Summarize the given text using OpenAI's language model."""
    try:
        llm = sdk.models.completions("yandexgpt").configure(temperature=0)

        messages = [
            {
                "role": "system",
                "text": "Найди наиболее точный ответ на вопрос и поясни его. Выбери только один правильный вариант из списка ниже. Если в источниках есть противоречивая информация, отдай приоритет первому достоверному источнику. После выбора ответа сравни его с остальными вариантами и убедись, что он соответствует условиям вопроса. \nФормат запроса: вопрос, две пустые строки, затем информация из интернета в виде (url + пустая строка + текст), разделяются так же двумя пустыми строками. Ответ выведи в виде сериализованного JSON. В поле answer выведи только номер ответа, если вопрос не подразумевает выбор ответа, то выведи null. В поле reasoning выведи подробное пояснение к ответу, как ты его получил и почему другие ответы не подходят. В поле sources выведи список url-сайтов, на которых ты нашел информацию.",
            },
            {
                "role": "user",
                "text": text,
            },
        ]
        result = llm.run(messages)
        return result[0].text.strip('\n` ')
    except Exception as e:
        print(f"Error in summarize_text: {str(e)}")
        return ""

def search_and_answer(query: str) -> str:
    """Perform a web search and summarize the results."""
    texts = search(query)
    text = query + '\n\n'
    for url, urlText in texts.items():
        text += url + '\n' + urlText + '\n\n'

    res = get_answer(text)
    return res