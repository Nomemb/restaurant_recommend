import pandas as pd
import numpy as np
import mongo_db

# df = pd.read_csv("../dataset/local_Restaurant_Keyword.csv", encoding='utf-8')
# df.to_json("../dataset/test.json", orient="records", force_ascii=False)

df = pd.read_json("../dataset/test.json", encoding='utf-8')
for store_info in df.itertuples():
    text = store_info.review.replace("[", "").replace("]", "").strip()

    reviews = [review.strip().strip("'") for review in text.split(",")]
    keyword = store_info.keyword.replace("[", "").replace("]", "").strip()

    # 맛집 기준
    if store_info.score <= 3.4:
        continue
        
    # 변환된 데이터를 딕셔너리 리스트로 재구성
    temp = {
        "store_name": f"{store_info.store_name}",
        "addr": f"{store_info.addr}",
        "score": f"{store_info.score}",
        "latitude": f"{store_info.latitude}",
        "longitude": f"{store_info.longitude}",
        "review": reviews,
        "keyword": store_info.keyword,
        "summary": f"{store_info.key_summary}"
    }
    mongo_db.insert_data(temp)
