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

def insert_data(store_info):
    # 월요일에 DB 연결하면 주석 해제
    # 이름과 주소가 중복되는 데이터 판별
    # db = connect_database()
    # existing_data = db.find_one({"store_name": store_info["store_name"], "addr": store_info["addr"]})
    #
    # if not existing_data:
    #     db.insert_one(store_info)
    #     print(f"{store_info['store_name']} data inserted")
    #
    # else:
    #     print(f"{store_info['store_name']} data already exists")
    # print(store_info)
    print(f"{store_info['store_name']} data inserted")
