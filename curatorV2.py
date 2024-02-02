from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# 서울 특별시 구 리스트
gu_list = ['마포구', '서대문구', '은평구', '종로구', '중구', '용산구', '성동구', '광진구', '동대문구', '성북구', '강북구', '도봉구', '노원구', '중랑구', '강동구', '송파구', '강남구', '서초구', '관악구', '동작구', '영등포구', '금천구', '구로구', '양천구', '강서구']

# CSV 파일 초기화 및 헤더 작성
cafes_file = 'cafes.csv'
reviews_file = 'reviews.csv'

with open(cafes_file, 'w', encoding='utf-8') as file:
    file.write("카페ID,카페명,주소,영업시간,전화번호\n")

with open(reviews_file, 'w', encoding='utf-8') as file:
    file.write("카페ID,리뷰\n")

# ChromeDriver 설정
chromedriver_path = r"C:\Users\seongmun\Desktop\윤성문\Honzapda_curator\chromedriver-win64\chromedriver.exe"
service = ChromeService(executable_path=chromedriver_path)
options = webdriver.ChromeOptions()
options.add_argument('lang=ko_KR')
driver = webdriver.Chrome(service=service, options=options)

cafe_id = 1  # 카페 고유 ID 초기화

def extract_and_save_reviews(cafe_id):
    # 리뷰를 추출하는 로직
    reviews = driver.find_elements(By.CSS_SELECTOR, ".list_evaluation > li")
    with open(reviews_file, 'a', encoding='utf-8') as file:
        for review in reviews:
            review_text = review.find_element(By.CSS_SELECTOR, ".comment_info > .txt_comment > span").text
            file.write(f"{cafe_id},\"{review_text}\"\n")

for gu_name in gu_list:
    driver.get('https://map.kakao.com/')
    search_area = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "search.keyword.query")))
    search_area.send_keys(gu_name + ' 카페')
    search_area.send_keys(Keys.ENTER)
    time.sleep(5)

    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".placelist > .PlaceItem")))

    cafes = driver.find_elements(By.CSS_SELECTOR, ".placelist > .PlaceItem")

    for cafe in cafes:
        cafe_name = cafe.find_element(By.CSS_SELECTOR, ".head_item > .tit_name > .link_name").text
        cafe_address = cafe.find_element(By.CSS_SELECTOR, ".info_item > .addr > p").text
        cafe_hours = "영업시간 정보 없음"
        cafe_phone = "전화번호 정보 없음"
        try:
            cafe_hours = cafe.find_element(By.CSS_SELECTOR, ".info_item > .openhour > p > a").text
            cafe_phone = cafe.find_element(By.CSS_SELECTOR, ".info_item > .contact > span").text
        except:
            pass

        with open(cafes_file, 'a', encoding='utf-8') as file:
            file.write(f"{cafe_id},{cafe_name},{cafe_address},{cafe_hours},{cafe_phone}\n")

        # 카페 상세 페이지로 이동하여 리뷰 수집
        cafe.find_element(By.CSS_SELECTOR, ".info_item > .contact > a.moreview").send_keys(Keys.ENTER)
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(3)

        extract_and_save_reviews(cafe_id)

        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        cafe_id += 1

driver.quit()
print("데이터 수집 완료")

