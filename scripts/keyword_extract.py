from konlpy.tag import Okt
import json
from textrank.textrank import KeywordSummarizer
import openai
from tqdm import tqdm
import pandas as pd


with open("./local.Restaurant.json", "r", encoding='utf-8') as f:
    data = json.load(f)


okt = Okt()
stop_word = ['하다', '것', '곳', '더', '가게', '거']
def okt_tokenizer(sent):
    words = okt.pos(sent, norm=True, stem=True)
    words = [w for w in words if ('Noun' in w or 'Verb' in w or 'Adjective' in w)]
    words = [w for w in words if not w[0] in stop_word]
    return words


for idx, rest in enumerate(data):
    summarizer = KeywordSummarizer(tokenize=okt_tokenizer, min_count=2, min_cooccurrence=1)
    try:
        rest['keyword'] = summarizer.summarize(rest['review'], topk=20)

    except:
        print(len(rest['review']))
        pass

print(f'리뷰가 너무 적은 식당은 제외한다.\n삭제 전 식당 개수 : {len(data)}')
for rest in data:
    if len(rest.keys()) == 7 :
        data.remove(rest)

print(f'삭제 후 식당 개수 : {len(data)}')


data_cp = data.copy()

api_key = "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"
client = openai.OpenAI(api_key=api_key)

for rest in tqdm(data_cp):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "너는 백종원 요리연구가처럼 동작구의 식당에 대해 잘 알고 있어. 너는 리뷰의 키워드를 추출한 결과만 보고 식당에 대해서 설명할 수 있어. 또한 동료 요리사에게 설명하듯이 쉽고 명료하게 설명해야 해. 150자 이내로 서술해줘."},
            {"role": "user", "content": f"""
          다음은 어떤 식당에 대한 리뷰에 대해서 textrank를 사용해 keyword를 추출한 결과야. 
          이걸 보고 이 식당에 대해서 140자로 간단하게 서술해줘.{rest['keyword']}"""}])

    rest["key_summary"] = response.choices[0].message.content

df = pd.DataFrame(data_cp, columns=data_cp[0].keys())
df = df.drop(axis=1, columns=['_id'])

df.to_csv('./local_Restaurant_Keyword.csv', index=False, encoding='utf-8')