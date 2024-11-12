from pymongo import MongoClient


def connect_database():
    # 기본 DB 연결
    client = MongoClient(host='localhost', port=27017)

    db = client['local']
    collection = db['Restaurant']
    return collection

# 데이터 찾기 예시
# print(collection.find_one({"name":"Alice"}))


def view_database(collection):
    # 모든 데이터 찾기
    all_documents = collection.find()
    for document in all_documents:
        print(document)


def validation_data(store_name, addr):
    if db.find_one({"store_name": store_name, "addr": addr}):
        print(f"{store_name} data already exists")
        return True

    else:
        return False


def insert_data(store_info):
    if not validation_data(store_info["store_name"], store_info["addr"]):
        db.insert_one(store_info)


db = connect_database()
