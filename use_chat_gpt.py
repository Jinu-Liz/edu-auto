import fitz
import tiktoken
from openai import OpenAI

PDF_PATH = "./[교안]하반기_정기안전보건교육.pdf"
GPT_MODEL = "gpt-3.5-turbo-16k"
API_KEY = "{OPENAI_API_KEY}"
client = OpenAI(api_key=API_KEY)


def ask_to_chat_gpt(jokbo, question):
    response = client.chat.completions.create(
        model=GPT_MODEL,
        messages=[
            {"role": "system", "content": "너는 시험을 보는 학생이야"},
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

            lecture_text = lecture_text + cur_text

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

    # question = """다음은 어떤 보험급여에 대한 설명인가? [업무상 사유로 부상, 질병으로 치유 후 장해가 있는 경우 지급되고, 신체에 정신적, 육체적 장해가 남아 장해급여 지급대상이 된다. 지급일수에 평균임금 곱하여 지급되고, 등급은 제1급~제14급까지 있다.] [ 25 점 ] 1 휴업급여 2 요양급여 3 장해급여 4 간병급여"""
    # question = question + "\n번호로만 대답해"
    # print(ask_to_chat_gpt(whole_text, question))

