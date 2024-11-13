from pymongo import MongoClient


def connect_database(db_name):
    # 기본 DB 연결
    client = MongoClient(host='localhost', port=27017)

    db = client['local']
    collection = db[db_name]
    return collection


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


def select_all_data():
    db = connect_database("Restaurant")
    cursor = db.find({})
    return cursor

# 실제용
# db = connect_database("Restaurant")
# 테스트용
db = connect_database("test_Restaurant")