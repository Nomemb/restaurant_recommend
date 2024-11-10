import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pandas as pd
import mongo_db

driver = webdriver.Chrome()

store = pd.read_csv("../dataset/store2.csv", encoding='utf-8')

drop_conditions = ['편의점', '푸드트럭', '출장조리', '라이브카페']
print(f"삭제 이전 : {len(store)}행")

store = store[~store.업태명.isin(drop_conditions)]
print(f"삭제 이후 : {len(store)}행")


# 카카오 맵으로 이동
url = "https://map.kakao.com/"
driver.get(url)
sample = store[:5]


def save_reviews():
    """
    :return: 리뷰들 리스트
    """
    review_list = []
    time.sleep(1)
    try:
        while True:
            # 후기 더보기 버튼이 있으면 계속 반복
            try:
                txt_more = driver.find_element(By.XPATH, '//span[@class="txt_more" and contains(text(), "후기 더보기")]')
                link_more_button = txt_more.find_element(By.XPATH, './ancestor::a[contains(@class, "link_more")]')

                if link_more_button and link_more_button.text != "후기 접기":
                    link_more_button.click()
                    # print("후기 더보기 클릭")

            # 없으면 탈출
            except:
                break

    except:
        print("후기 더보기 버튼 없음")

    # 리뷰들 긁어오기
    time.sleep(5)
    reviews = driver.find_elements(By.CLASS_NAME, 'txt_comment')
    for review in reviews:
        # 더보기 죽이기
        txt = review.text.replace("더보기" ,"")
        txt = txt.replace("\n", " ")
        # 별점만 남긴 리뷰는 저장하지 않음
        if len(txt) != 0 :
            review_list.append(txt)

    # 다시 검색창으로 이동
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    time.sleep(1)

    return review_list


def insert_data_to_database(dataframe):
    """
    :param dataframe: 리뷰 검색을 위한 데이터프레임
    :return mongoDB에 데이터를 전달해주는 함수
    """
    for store_name, addr in zip(dataframe["업소명"], dataframe["addr"]):
        # 카카오맵 검색창
        search_area = driver.find_element(By.ID, "search.keyword.query")
        # 기존 검색어 제거
        search_area.clear()
        # 검색어 전달
        search_area.send_keys(addr)

        # 돋보기 클릭(검색)
        driver.find_element(By.XPATH, r'//*[@id="search.keyword.submit"]').send_keys(Keys.ENTER)

        time.sleep(1)

        try:
            num_of_result = int(
                driver.find_element(By.XPATH, '/html/body/div[5]/div[2]/div[1]/div[7]/div[5]/div[1]/span/em').text)
            if num_of_result > 5:
                # 장소 더보기 클릭
                try:
                    driver.find_element(By.XPATH,'//a[@id="info.search.place.more" and contains(text(), "장소 더보기")]').send_keys(Keys.ENTER)

                except:
                    continue

        except:
            continue

        # 결과창 전부 받아옴
        # same_list = driver.find_elements(By.CSS_SELECTOR, "//a[@class='link_name']").text
        for t in range(1, num_of_result + 1):
            xpath_name = f'/html/body/div[5]/div[2]/div[1]/div[7]/div[5]/ul/li[{t}]/div[3]/strong/a[2]'
            name = driver.find_element(By.XPATH, xpath_name).text

            try:
                xpath_review = f'/html/body/div[5]/div[2]/div[1]/div[7]/div[5]/ul/li[{t}]/div[4]/span[1]/a'
                review_num = int(driver.find_element(By.XPATH, xpath_review).text[:-1])

                xpath_score = f'/html/body/div[5]/div[2]/div[1]/div[7]/div[5]/ul/li[{t}]/div[4]/span[1]/em'
                score = float(driver.find_element(By.XPATH, xpath_score).text)

                if name == store_name and review_num >= 5:
                    print(f"{name}: 음식점 저장 --- {score}점(리뷰 {review_num}개)")

                    ### 리뷰 크롤링
                    # 리뷰 건수를 눌러서 리뷰 탭으로 이동
                    driver.find_element(By.XPATH, xpath_review).send_keys(Keys.ENTER)
                    driver.switch_to.window(driver.window_handles[-1])
                    time.sleep(1)

                    reviews = save_reviews()
                    temp = {
                        "store_name":store_name,
                        "addr":addr[:-1],
                        "score":score,
                        "review":reviews
                    }
                    mongo_db.insert_data(temp)

            except:
                # 다시 검색창으로 이동
                driver.switch_to.window(driver.window_handles[0])
                time.sleep(.5)
                pass
