from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pandas as pd
import mongo_db
import time
import re


def set_driver():
    driver = webdriver.Chrome()
    # 카카오 맵으로 이동
    url = "https://map.kakao.com/"
    driver.get(url)

    return driver


def regex_addr(addr):
    addr = addr.strip()
    p1 = re.compile(r'서울특별시 동작구 [가-힣]+\d*동 ([가-힣]*\s*)(\d+[-]*\d*)(\s[a-z]*[가-힣]*)*')
    m1 = p1.search(addr)
    x = addr[:m1.end()]
    x = re.sub(r'외', '', x)
    x = re.sub(r'지하 ', '', x)
    x = x.strip()
    return x


driver = set_driver()
store = pd.read_csv("../dataset/store2.csv", encoding='utf-8')

drop_conditions = ['편의점', '푸드트럭', '출장조리', '라이브카페']
print(f"삭제 이전 : {len(store)}행")

store = store[~store.업태명.isin(drop_conditions)]


# 주소 전처리
non_str_indices = store.loc[store['addr'].apply(lambda x: not isinstance(x, str)), 'addr'].index
store = store.drop(non_str_indices, axis=0).reset_index(drop=True)
print(f"삭제 이후 : {len(store)}행")
addr_clean = []
for addr in store.addr:
    cleaned_addr = regex_addr(addr)
    addr_clean.append(cleaned_addr)
store['addr'] = addr_clean

store.to_csv("../dataset/clean_store_data.csv", encoding='utf-8')

store = pd.read_csv("../dataset/clean_store_data.csv", encoding='utf-8')

temp = store.copy()
print(temp.info)
temp.drop_duplicates(["업소명","addr"], inplace=True)
print(temp.info)

sample = store[1786:8172]


def save_reviews():
    """
    :return: 리뷰들 리스트
    """
    review_list = []
    try:
        while True:
            # 후기 더보기 버튼이 있으면 계속 반복
            try:
                txt_more = driver.find_element(By.XPATH, '//span[@class="txt_more" and contains(text(), "후기 더보기")]')
                link_more_button = txt_more.find_element(By.XPATH, './ancestor::a[contains(@class, "link_more")]')

                if link_more_button and link_more_button.text != "후기 접기":
                    link_more_button.click()
                    time.sleep(0.5)
                    # print("후기 더보기 클릭")

            # 없으면 탈출
            except:
                break

    except:
        print("후기 더보기 버튼 없음")

    time.sleep(3)
    # 리뷰들 긁어오기
    reviews = driver.find_elements(By.CLASS_NAME, 'txt_comment')

    for review in reviews:
        # 더보기 죽이기
        txt = review.text.replace("더보기" ,"").replace("\n", " ")

        # 별점만 남긴 리뷰는 저장하지 않음
        if len(txt) != 0:
            review_list.append(txt)

    # 다시 검색창으로 이동
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    time.sleep(1)
    return review_list


def crawl_rest_data(num_of_result, store_name, addr, latitude, longitude):
    for t in range(1, min(16, 1 + num_of_result)):
        xpath_name = f'/html/body/div[5]/div[2]/div[1]/div[7]/div[5]/ul/li[{t}]/div[3]/strong/a[2]'
        try:
            name = driver.find_element(By.XPATH, xpath_name).text
            xpath_review = f'/html/body/div[5]/div[2]/div[1]/div[7]/div[5]/ul/li[{t}]/div[4]/span[1]/a'
            review_num = int(driver.find_element(By.XPATH, xpath_review).text[:-1])
            xpath_score = f'/html/body/div[5]/div[2]/div[1]/div[7]/div[5]/ul/li[{t}]/div[4]/span[1]/em'
            score = float(driver.find_element(By.XPATH, xpath_score).text)

            if name == store_name and review_num >= 5:
                if mongo_db.validation_data(store_name, addr):
                    raise Exception()

                print(f"{name}: 음식점 저장 --- {score}점(리뷰 {review_num}개)")
                ### 리뷰 크롤링
                # 리뷰 건수를 눌러서 리뷰 탭으로 이동

                driver.find_element(By.XPATH, xpath_review).send_keys(Keys.ENTER)
                driver.switch_to.window(driver.window_handles[-1])
                time.sleep(5)
                reviews = save_reviews()
                temp = {
                    "store_name": store_name,
                    "addr": addr,
                    "score": score,
                    "latitude": latitude,
                    "longitude": longitude,
                    "review": reviews
                }
                mongo_db.insert_data(temp)
        except:
            # 다시 검색창으로 이동
            driver.switch_to.window(driver.window_handles[0])
            time.sleep(2)
            pass


def insert_data_to_database(dataframe):
    """
    :param dataframe: 리뷰 검색을 위한 데이터프레임
    :return mongoDB에 데이터를 전달해주는 함수
    """
    global driver
    cnt = 0
    for store_name, addr, latitude, longitude in zip(dataframe["업소명"],
                                                     dataframe["addr"],
                                                     dataframe["latitude"],
                                                     dataframe["longitude"]):
        # 메모리 누수 버그 잡기
        if cnt == 20:
            cnt = 0
            driver = set_driver()

        cnt += 1

        # 카카오맵 검색창
        search_area = driver.find_element(By.ID, "search.keyword.query")
        # 기존 검색어 제거
        search_area.clear()
        # 검색어 전달
        search_area.send_keys(addr)

        # 돋보기 클릭(검색)
        driver.find_element(By.XPATH, r'//*[@id="search.keyword.submit"]').send_keys(Keys.ENTER)
        time.sleep(2)

        try:
            num_of_result = int(
                driver.find_element(By.XPATH, '/html/body/div[5]/div[2]/div[1]/div[7]/div[5]/div[1]/span/em').text)
            if num_of_result > 5:
                # 장소 더보기 클릭
                try:
                    driver.find_element(By.XPATH,'//a[@id="info.search.place.more" and contains(text(), "장소 더보기")]').send_keys(Keys.ENTER)
                    time.sleep(0.5)

                except:
                    continue

        except:
            continue

        # 결과창 전부 받아옴
        n = num_of_result // 15 + (1 if num_of_result % 15 > 0 else 0)

        if n == 1:
            crawl_rest_data(num_of_result, store_name, addr, latitude, longitude)
        elif n > 5:
            pass
        else:
            for i in range(1, n + 1):
                try:
                    driver.find_element(By.XPATH,
                                        f'//a[@id="info.search.page.no{i}" and contains(text(), "{i}")]').send_keys(
                        Keys.ENTER)
                    time.sleep(1)
                    crawl_rest_data(num_of_result, store_name, addr, latitude, longitude)
                    num_of_result -= 15
                except:
                    continue


# 시간 테스트용) 100개 458초 걸림.
start = time.time()
insert_data_to_database(sample)
end = time.time()
print(f"{end - start:.5f} sec")