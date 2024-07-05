import fitz
import tiktoken
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

PDF_PATH = "./jokbo/" + os.environ.get("JOKBO_FILE") + ".pdf"
GPT_MODEL = "gpt-4-turbo"
API_KEY = os.environ.get("API_KEY")
client = OpenAI(api_key=API_KEY)


def ask_to_chat_gpt(jokbo, question):
    response = client.chat.completions.create(
        model=GPT_MODEL,
        messages=[
            {"role": "system", "content": "너는 안전보건 전문가야"},
            {"role": "user", "content": jokbo + '\n' + question}
        ]
    )

    return response.choices[0].message.content[0]


def count_use_token(text: str):
    encoder = tiktoken.encoding_for_model(GPT_MODEL)

    token_list = encoder.encode(text)
    print(token_list)
    print(len(token_list))


def get_jokbo_dic():
    doc = fitz.open(PDF_PATH)
    lec_dic = {}
    lecture_text = ''
    part_num = 0
    for page in doc:
        text = page.get_text()
        text_list = text.split('\n')
        for cur_text in text_list:
            if '차시]' in cur_text:
                lec_dic[part_num] = lecture_text

                lecture_text = ''
                part_num = part_num + 1
                continue

            lecture_text = lecture_text + '\n' + cur_text

    lec_dic[part_num] = lecture_text

    return lec_dic


if __name__ == '__main__':
    lec_dic = get_jokbo_dic()
    whole_text = ''
    for text in lec_dic.values():
        whole_text += text

    encoder = tiktoken.encoding_for_model(GPT_MODEL)
    token_list = encoder.encode(whole_text)

    print(len(token_list))

    question = """심폐소생술에 대한 설명으로 아닌 것은? [ 25 점 ] 1 분당 100~120회의 속도로 가슴을 압박한다. 2 다른 사람에게 양도한다. 3 가슴 압박 중단은 최소화하며 5주기마다 압박자를 교체한다. 4 5~6cm 깊이로 가슴을 압박한다."""
    question = question + "\n번호로만 대답해"
    print(ask_to_chat_gpt(whole_text, question))

