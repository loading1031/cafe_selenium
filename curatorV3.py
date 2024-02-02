from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException
import time

# 서울 특별시 구 리스트
gu_list = ['공덕']

# CSV 파일 초기화 및 헤더 작성
cafes_file = 'cafesV3.csv'
reviews_file = 'reviewsV3.csv'

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
    more_reviews_buttons = driver.find_elements(By.CSS_SELECTOR, ".txt_more")
    total = len(more_reviews_buttons) # 시작 버튼 갯수
    # "후기 더보기" 버튼을 클릭할 수 있는 동안 계속 클릭하기
    while True:    
        try:
            more_reviews_buttons = driver.find_elements(By.CSS_SELECTOR, ".txt_more")
            print("total: "+str(total)+" 지금 갯수: "+str(len(more_reviews_buttons)))
            if len(more_reviews_buttons)!=total: 
                break  # 더 보기 버튼수가 달라지면 반복 종료
           
            any_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".txt_more"))
            )
            any_button.click()
            # 페이지가 새로운 리뷰를 로드할 시간을 주기 위해 잠시 대기
            time.sleep(3)
        except (NoSuchElementException, TimeoutException):
            print("모든 더보기 버튼이 없음")
            # 더 이상 "후기 더보기" 버튼이 없으면 반복 종료
            break
        except ElementClickInterceptedException:
            print("클릭할 수 없는 상태")
        # 클릭할 수 없는 상태일 때 예외 처리하여 반복문 종료
            break

    # 리뷰를 추출하는 로직
    reviews = driver.find_elements(By.CSS_SELECTOR, ".list_evaluation > li")
    with open(reviews_file, 'a', encoding='utf-8') as file:
        for review in reviews:
            review_text = review.find_element(By.CSS_SELECTOR, ".comment_info > .txt_comment > span").text
            file.write(f"{cafe_id},\"{review_text}\"\n")

driver.get('https://map.kakao.com/')
search_area = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "search.keyword.query")))
search_area.send_keys(gu_list[0] + ' 카페')
search_area.send_keys(Keys.ENTER)
time.sleep(5)

time.sleep(5)
WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".placelist > .PlaceItem")))

current_page = 1
last_page_reached = False

def go_to_next_group_page():
    print("다음 그룹 페이지로 이동 시도")
    try:
        # 다음 그룹 페이지 버튼 클릭 로직은 기본적으로 동일하나, 페이지 로드 완료를 보장하기 위한 대기 로직 추가 필요
        next_group_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "info.search.page.next"))
        )
        driver.execute_script("arguments[0].click();", next_group_button)
        time.sleep(5)  # 새 페이지 로드 대기
        print("다음 그룹 페이지로 성공적으로 이동")
        return False
    except TimeoutException:
        print("다음 그룹 페이지 버튼이 없습니다. 마지막 페이지 그룹으로 간주합니다.")
        return True

def go_to_next_page(current_page):
    try:
        print("current_page:%d\n",current_page)
        next_page_btn_id = "info.search.page.no{}".format(current_page)
        next_page_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, next_page_btn_id))
        )
        driver.execute_script("arguments[0].click();", next_page_button)
        time.sleep(5)  # 새 페이지 로드 대기
        return False
    
    except (NoSuchElementException, TimeoutException) as e:
        return go_to_next_group_page()

try:
    while not last_page_reached:
        
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
        
        if(current_page==1):
            try:
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "info.search.place.more"))
                    and EC.visibility_of_element_located((By.ID, "info.search.place.more"))
                )

                driver.execute_script("arguments[0].click();", element)
                current_page += 1
                # 페이지가 새로운 카페 리스트를 로드할 시간을 주기 위해 잠시 대기
                time.sleep(5)
            except NoSuchElementException:
                last_page_reached = True

        else :
             current_page = current_page - 4 if current_page+1 > 6 else current_page + 1
             last_page_reached=go_to_next_page(current_page)

            
except Exception as e:
    print(f"오류 발생: {e}")
finally:
    driver.quit()

# driver.quit()
print("데이터 수집 완료")