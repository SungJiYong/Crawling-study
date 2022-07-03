import re
import time
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import requests
import csv
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import googlemaps
import pandas as pd

import sys

import pymysql
import pandas
from haversine import haversine

# 크롬 드라이버 무설치 활용에 필요한 코드

from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import ElementNotInteractableException
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(ChromeDriverManager().install())
service = Service(executable_path=ChromeDriverManager().install())

headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.108 Whale/3.15.136.18 Safari/537.36"}



    
#현재파일에 있는 크롬 드라이버 가져와서 열기
options = webdriver.ChromeOptions()
options.add_experimental_option("exclusiveSwitches", ["enable-logging"]) #USB에러 해결 코드
# options.add_argument('headless') #브라우저 안 띄우기
options.add_argument('lang=ko_KR') #언어 KR
chromedriver_path = "chromedriver" #크롬드라이버 위치



#크롬 창 설정 완료


##########################################
#검색어 입력 및 준비
##########################################


#1. 카카오 지도로 이동, input 내용 입력
url = "https://map.kakao.com/"
driver.get(url)
time.sleep(1)

# 현위치 자동화 어떻게 하지?
# youat = input("현위치 입력 : ")
# youat = "강남구 삼성2동 144-26"
youat = "서울 관악구 봉천로 569"
# searchloc = input("맛집 검색 지역 입력 : ")
# searchloc = "강남구 삼성동 음식점"
searchloc = "관악구 낙성대 카페"

#2. 음식점 입력 후 찾기 버튼 클릭 xpath활용
search_area = driver.find_element_by_xpath('//*[@id="search.keyword.query"]') #검색창
search_area.send_keys(searchloc)
driver.find_element_by_xpath('//*[@id="search.keyword.submit"]').send_keys(Keys.ENTER) #enter로 검색

time.sleep(1)


#3. 장소 버튼 클릭(장소버튼을 클릭해야 페이지별 크롤링 가능)
driver.find_element_by_xpath('//*[@id="info.main.options"]/li[2]/a').send_keys(Keys.ENTER)

##########################################
#음식점 이름, 평점, 리뷰 등 정보 저장 함수
#상세페이지
##########################################
cafe_list=[]
menu_list=[]

html = driver.page_source # 페이지의 elements모두 가져오기
soup = BeautifulSoup(html, 'html.parser') # BeautifulSoup사용하기

def rec_menuInfo():
    print("222")
    for i in range(0,15):
        getMenuInfo(i)
        print("999")
        driver.close()
        driver.switch_to.window(driver.window_handles[0])  # 검색 탭으로 전환
    print("101010")
    f=open('menu_name.csv',"w",encoding="utf-8-sig",newline="")
    writecsv = csv.writer(f)
    header=['code','Name','menu','price']
    writecsv.writerow(header)

    for k in menu_list:
        writecsv.writerow(k)

def getMenuInfo(i):
    
    print(i+1, '번째 음식점 기록중')
    if i<3:
        detail_page_xpath = '//*[@id="info.search.place.list"]/li[' + str(i + 1) + ']'
        driver.find_element_by_xpath(f'{detail_page_xpath}/div[5]/div[4]/a[1]').send_keys(Keys.ENTER)
        driver.switch_to.window(driver.window_handles[-1])  # 탭은 자동으로 전환되지만 driver의 주소를 전환시켜주는 기능으로 필수적용
    elif i >= 3:
        detail_page_xpath_add = '//*[@id="info.search.place.list"]/li[' + str(i + 2) + ']'
        driver.find_element_by_xpath(f'{detail_page_xpath_add}/div[5]/div[4]/a[1]').send_keys(Keys.ENTER)
        driver.switch_to.window(driver.window_handles[-1])  # 탭은 자동으로 전환되지만 driver의 주소를 전환시켜주는 기능으로 필수적용
    print("222-2")
    time.sleep(1)

    html = driver.page_source # 페이지의 elements모두 가져오기
    soup = BeautifulSoup(html, 'html.parser') # BeautifulSoup사용하기
    print("333")
    getCafeInfo()
    print("888")
    # 메뉴의 3가지 타입
    menuonlyType = soup.select('.cont_menu > .list_menu > .menuonly_type')
    nophotoType = soup.select('.cont_menu > .list_menu > .nophoto_type')
    photoType = soup.select('.cont_menu > .list_menu > .photo_type')

    if len(menuonlyType) != 0:
        for soup in menuonlyType:
            menu_list.append(_getMenuInfo(soup))
    elif len(nophotoType) != 0:
        for soup in nophotoType:
            menu_list.append(_getMenuInfo(soup))
    else:
        for soup in photoType:
            menu_list.append(_getMenuInfo(soup))
    
    return menu_list

def getCafeInfo():
    time.sleep(0.5)
    print("444")

    temp=[]
    cafe_name = driver.find_element_by_xpath('//*[@id="mArticle"]/div[1]/div[1]/div[2]/div/h2').text
    food_type = driver.find_element_by_xpath('//*[@id="mArticle"]/div[1]/div[1]/div[2]/div/div/span[1]').text

    if driver.find_element_by_xpath('//*[@id="mArticle"]/div[1]/div[1]/div[2]/div/div/span[3]').text == "후기미제공":
        food_score = "후기미제공"
    else:
        food_score = driver.find_element_by_xpath('//*[@id="mArticle"]/div[1]/div[1]/div[2]/div/div/a[1]/span[1]').text

    if food_score == "후기미제공":
        review = driver.find_element_by_xpath('//*[@id="mArticle"]/div[1]/div[1]/div[2]/div/div/a/span').text
    else:
        review = driver.find_element_by_xpath('//*[@id="mArticle"]/div[1]/div[1]/div[2]/div/div/a[2]/span').text
    print("444-1")
    addr = driver.find_element_by_xpath('//*[@id="mArticle"]/div[1]/div[2]/div[1]/div/span[1]').text
    addr_simple = driver.find_element_by_xpath('//*[@id="mArticle"]/div[1]/div[2]/div[1]/div/span[2]').text
    print("555")
    # //*[@id="mArticle"]/div[1]/div[2]/div[2]/div #공통부
    distin = driver.find_element_by_xpath('//*[@id="mArticle"]/div[1]/div[2]/div[2]/div').text

    if "영업중" in distin:
        cafe_operating = driver.find_element_by_xpath('//*[@id="mArticle"]/div[1]/div[2]/div[2]/div/div[1]/strong/span').text
        cafe_op_hour = driver.find_element_by_xpath('//*[@id="mArticle"]/div[1]/div[2]/div[2]/div/div[1]/ul/li/span').text
    elif "금일영업마감" in distin:
        cafe_operating = driver.find_element_by_xpath('//*[@id="mArticle"]/div[1]/div[2]/div[2]/div/div[1]/strong/span').text
        cafe_op_hour = driver.find_element_by_xpath('//*[@id="mArticle"]/div[1]/div[2]/div[2]/div/div[1]/ul/li/span').text
    elif "임시휴업" in distin:
        cafe_operating = driver.find_element_by_xpath('//*[@id="mArticle"]/div[1]/div[2]/div[2]/div/div/strong/span').text
        cafe_op_hour = driver.find_element_by_xpath('//*[@id="mArticle"]/div[1]/div[2]/div[2]/div/div/ul/li/span').text
    elif "휴무일" in distin:
        cafe_operating = driver.find_element_by_xpath('//*[@id="mArticle"]/div[1]/div[2]/div[2]/div/div[1]/strong/span').text
        cafe_op_hour = driver.find_element_by_xpath('//*[@id="mArticle"]/div[1]/div[2]/div[2]/div/div[1]/ul/li/span').text
    else:
        cafe_operating = "null data"
        cafe_op_hour = "null data"

        
    print("666")
    link = driver.find_element_by_xpath('/html/head/meta[8]').text
    print(link)

    #우편번호 제거
    addr = addr[:-9]

    #거리 정보에서 (지번) 제거
    addr_simple = addr_simple[2:len(addr_simple)]
    print(addr_simple)
    #음식점 거리 정보
    cafe_coord = get_location(addr_simple)

    #현위치 정보
    at_coord = get_location(youat)

    #거리 비교
    walking_speed = 67 #m/min
    bt_dist = haversine(cafe_coord,at_coord,unit='m') #m
    esti_time = int(bt_dist / walking_speed * 1.5) #min 허용치 1.5배 부여(최단거리가 아닌 블럭형 도심지 특성)

    temp.append(cafe_name)
    temp.append(food_type)
    temp.append(cafe_operating)
    temp.append(cafe_op_hour)
    temp.append(food_score)
    temp.append(review)
    temp.append(link)
    temp.append(addr)
    temp.append(esti_time)

    cafe_list.append(temp)
    print("777")
    f=open('cafe_name.csv',"w",encoding="utf-8-sig",newline="")
    writecsv = csv.writer(f)
    header=['Name','Type','open','hour','Score','Review','Link','Addr','dis(min)']
    writecsv.writerow(header)

    for n in cafe_list:
        writecsv.writerow(n)

def _getMenuInfo(soup):
    cafe_Code = ""
    cafe_Title = driver.find_element_by_xpath('//*[@id="mArticle"]/div[1]/div[1]/div[2]/div/h2').text
    menuName = soup.select('.info_menu > .loss_word')[0].text
    menuPrices = soup.select('.info_menu > .price_menu')
    menuPrice = ''

    if len(menuPrices) != 0:
        menuPrice =  menuPrices[0].text.split(' ')[1]

    return [cafe_Code, cafe_Title, menuName, menuPrice]

# 위치정보 정의
import requests, json
def get_location(address):
  url = 'https://dapi.kakao.com/v2/local/search/address.json?query=' + address
  headers = {"Authorization": "KakaoAK 649cf02c93135dcdca7ce82c113f89a6"}
  api_json = json.loads(str(requests.get(url,headers=headers).text))
  address = api_json['documents'][0]['address']
  loaction_coord = (float(address['y']), float(address['x']))

  return loaction_coord


##########################################
#페이지들 돌아가며 크롤링
##########################################


page=1
page2=0

#1페이지부터 34페이지까지 출력
for i in range(0,40):
    #페이지 넘어가며 출력
    try:
        print("000")
        page2+=1
        print("**",page,"**")
        driver.find_element_by_xpath(f'//*[@id="info.search.page.no{page2}"]').send_keys(Keys.ENTER)
        print("111")
        rec_menuInfo()
        print("111111")
        if (page2)%5==0:
            driver.find_element_by_xpath(f'//*[@id="info.search.page.next"]').send_keys(Keys.ENTER)
            page2=0
        page+=1
            
    except:
        break


driver.close() #url = "https://map.kakao.com/"를 꺼주는 명령

print("**크롤링 완료**")

        
