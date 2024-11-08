from pymongo import MongoClient

# 기본 DB 연결
client = MongoClient(host='localhost', port=27017)

db = client['local']
collection = db['Restaurant']

# 데이터 찾기 예시
# print(collection.find_one({"name":"Alice"}))


# 모든 데이터 찾기
all_documents = collection.find()
for document in all_documents:
    print(document)