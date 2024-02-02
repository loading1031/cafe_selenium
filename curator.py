from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import os

# 서울 특별시 구 리스트
gu_list = ['마포구', '서대문구', '은평구', '종로구', '중구', '용산구', '성동구', '광진구', '동대문구', '성북구', '강북구', '도봉구', '노원구', '중랑구', '강동구', '송파구', '강남구', '서초구', '관악구', '동작구', '영등포구', '금천구', '구로구', '양천구', '강서구']

# CSV 파일 초기화 및 헤더 작성
fileName = 'test.csv'
with open(fileName, 'w', encoding='utf-8') as file:
    file.write("카페명|주소|영업시간|전화번호|대표사진주소\n")

# ChromeDriver 설정
chromedriver_path = r"C:\Users\seongmun\Desktop\윤성문\Honzapda_curator\chromedriver-win64\chromedriver.exe"
service = ChromeService(executable_path=chromedriver_path)
options = webdriver.ChromeOptions()
options.add_argument("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36")
options.add_argument('lang=ko_KR')
driver = webdriver.Chrome(service=service, options=options)

for gu_name in gu_list:
    driver.get('https://map.kakao.com/')
    search_area = driver.find_element(By.ID, "search.keyword.query")
    search_area.send_keys(gu_name + ' 카페')
    driver.find_element(By.ID, "search.keyword.submit").send_keys(Keys.ENTER)
    time.sleep(3)  # 동적 페이지 로딩 대기
    
    # 더보기 페이지 진입
    try:
        more_page = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "info.search.place.more")))
        more_page.click()
        time.sleep(2)
    except Exception as e:
        print(f"{gu_name}: 더보기 페이지 로드 실패 - {e}")
        continue

    # 페이지 내 정보 수집
    while True:
        place_lists = driver.find_elements(By.CSS_SELECTOR, r'#info\.search\.place\.list > li')
        for place in place_lists:
            html_content = place.get_attribute('innerHTML')
            soup = BeautifulSoup(html_content, "html.parser")
            
            # 정보 추출
            place_name = soup.select_one('.head_item > .tit_name > .link_name').text.strip()
            place_address = soup.select_one('.info_item > .addr > p').text.strip()
            place_hour = soup.select_one('.info_item > .openhour > p > a').text.strip() if soup.select_one('.info_item > .openhour > p > a') else '시간 정보 없음'
            place_tel = soup.select_one('.info_item > .contact > span').text.strip() if soup.select_one('.info_item > .contact > span') else '전화번호 정보 없음'

            # CSV 파일에 저장
            with open(fileName, 'a', encoding='utf-8') as file:
                file.write(f"{place_name}|{place_address}|{place_hour}|{place_tel}|\n")

            # 카페 상세 페이지로 이동하는 링크 클릭
            detail_link = place.find_element(By.CSS_SELECTOR, '.tit_name > .link_name')
            detail_link.click()
            time.sleep(3)  # 상세 페이지 로딩 대기

            # 리뷰 탭으로 이동
            driver.switch_to.window(driver.window_handles[1])  # 새 탭으로 이동
            try:
                review_tab = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '리뷰 탭 선택자'))
                )
                review_tab.click()
                time.sleep(2)

                # 리뷰 정보 수집
                reviews = driver.find_elements(By.CSS_SELECTOR, '리뷰 정보 선택자')
                for review in reviews:
                    # 리뷰 정보 추출 및 저장 로직...
                    pass

            except Exception as e:
                print(f"{gu_name}: 리뷰 탭 이동 실패 - {e}")
            finally:
                driver.close()  # 상세 페이지 탭 닫기
                driver.switch_to.window(driver.window_handles[0])  # 원래 탭으로 돌아가기    
                
        # 다음 페이지로 이동
        try:
            next_btn = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.ID, "info.search.page.next")))
            if "disabled" in next_btn.get_attribute("class"):
                print(f"{gu_name}: 더 이상 페이지가 없습니다.")
                break  # 다음 페이지가 없으면 반복 중단
            else:
                next_btn.click()  # 다음 페이지가 있으면 클릭하여 페이지 이동
                time.sleep(2)  # 페이지 로딩 대기
        except Exception as e:
            print(f"{gu_name}: 다음 페이지 이동 중 오류 발생 - {e}")
            break  # 오류 발생 시 반복 중단

driver.quit()  # 모든 작업 완료 후 드라이버 종료
print("데이터 수집 완료")

