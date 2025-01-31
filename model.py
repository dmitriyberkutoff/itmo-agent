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
                "text": "Ты отлично знаешь информацию об университете ИТМО и хорошо ищешь ее в имточниках. Тебе на вход подается вопрос и источники, в которых нужно найти на него ответ. Приоритет нужно отдавать официальным источникам ИТМО (itmo.ru, news.itmo.ru). В вопросе могут быть варианты ответа (их порядок не важен), а могут не быть. Тебе нужно дать правильный ответ на вопрос в виде сериализованного JSON. Если варианты ответа были предложены в самом вопросе, то в поле answer напиши номер правильного варианта ответа, а если вариантов не было, напиши в поле answer null. В поле reasoning напиши подробный, развернутый ответ с пояснением, как ты его получил, а последним предложением добавь, что информация получена с помощью YandexGPT. В поле sources указать список url источников, на которых ты нашел ответ. Не нужно запоминать контекст прошлых вопросов и ответов.",
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