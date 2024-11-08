import time
import warnings
warnings.filterwarnings('ignore')

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pandas as pd

driver = webdriver.Chrome()
store = pd.read_csv("./store.csv", encoding='utf-8')
cond1 = store.업태명 == '편의점'
cond2 = store.업태명 == '푸드트럭'
cond3 = store.업태명 == '출장조리'
cond4 = store.업태명 == '라이브카페'
drop_idx = store.loc[cond1 | cond2 | cond3 | cond4 ].index
store = store.drop(drop_idx)


# 카카오 맵으로 이동
url = "https://map.kakao.com/"
driver.get(url)
sample = store[:10]
rest_dict = {}

def save_reviews():
    """
    :param url: 리뷰 추출할 웹 사이트 주소
    :return: 리뷰들 리스트
    """
    # review_dict = {}
    # driver = webdriver.Chrome()
    # driver.get(url)
    review_list = []
    time.sleep(2)
    try:
        while True:
            # 후기 더보기 버튼이 있으면 계속 반복
            try:
                txt_more = driver.find_element(By.XPATH, '//span[@class="txt_more" and contains(text(), "후기 더보기")]')
                link_more_button = txt_more.find_element(By.XPATH, './ancestor::a[contains(@class, "link_more")]')
                time.sleep(.5)

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
    time.sleep(2)

    return review_list


for store_name, addr in zip(sample["업소명"], sample["addr"]):
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
                time.sleep(2)
            except:
                continue
        # num_of_result = min(5, num_of_result)
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

                temp = dict()
                temp["store_name"] = store_name
                temp["addr"] = addr[:-1]
                temp["score"] = score

                ### 리뷰 크롤링
                # 리뷰 건수를 눌러서 리뷰 탭으로 이동
                driver.find_element(By.XPATH, xpath_review).send_keys(Keys.ENTER)
                driver.switch_to.window(driver.window_handles[-1])
                time.sleep(5)

                temp["review"] = save_reviews()
                rest_dict.add(temp)

        except:
            # 다시 검색창으로 이동
            driver.switch_to.window(driver.window_handles[0])
            time.sleep(2)
            pass

### dataframe으로 변환 후 csv 추출
