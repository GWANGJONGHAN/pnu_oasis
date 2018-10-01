import os
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import math
import time

sidoMap = {'2611010200': '중구 중앙동'}
map = open("sido_map.csv", "r", encoding='UTF8')
k = 0
while True:
    line = map.readline()
    if not line: break
    temp = line.split(",")
    if k is 0:
        pass
    sidoMap[str(temp[2].strip())] = str(temp[0]+ " " + temp[1])
map.close()
busan_dong = list()
for key, val in sidoMap.items():
    busan_dong.append(val)
busan_dong[0] = '중구 중앙동'
busan_dong=list(set(busan_dong))


def classifierPublic(txt):
    if txt.find("공영")>0:
        result = "public"
    else:
        result = "private"
    return result

excess_gu =[]
error_gu = []
parking_area_name = []
parking_area_posession =[]
parking_area_address = []

driver2 = webdriver.Firefox()

f = open("중간과정.csv", "w")
index = 0
for section_num in range(len(busan_dong)):
    for public_or_private in range(2):
        if public_or_private == 0:
            pubpri = "공영"
        else:
            pubpri = "민영"
        try:
            url = "http://map.naver.com/?query="+str(busan_dong[section_num])+"+"+pubpri+"+주차장"

            driver2.get(url)
            path = "/html/body/div[3]/div[2]/div[1]/div[2]/div[2]/div[1]/div[2]/div[1]/div[2]/h2/span/em"
            page_num2 = driver2.find_element_by_xpath(path)
            page_num = int(page_num2)
            print(page_num)
        except:
            break;
        
        if page_num>310:
            print(busan_dong[section_num]+" : "+pubpri+" : "+str(page_num))
            excess_gu.append(busan_dong[section_num]+" : "+pubpri+" : "+str(page_num))
            page_num =  31
            print(page_num)
            
        else:
            page_num = math.ceil(page_num/10)
            print(page_num)
        
        for j in range(0,page_num):
            index = 0
            time.sleep(2.5)
            try:
                time.sleep(1)
                url = "http://map.naver.com/?query="+str(busan_dong[section_num])+" 주차장"+"&page="+str(j+1)
                print(url)
                driver2.get(url)    
            
            except NoSuchElementException:
                    print("-"*10)
                    print("not found")
                    print("-"*10)
                    error_gu.append("not found "+url)
        
            except IndexError:
                    print("-"*10)
                    print("IndexError")
                    print("-"*10)
                    error_gu.append("indexError "+url)
            
            for i in range(10):
                try:
            #주차장 이름
                    k = i+1
                    k = str(k)
                    path = "/html/body/div[3]/div[2]/div[1]/div[2]/div[2]/div[1]/div[2]/div[2]/ul/li["+k+"]/div[1]/dl/dt/a"
                    name = driver2.find_element_by_xpath(path)
                    name = name.text
                    print(name)
                    parking_area_name.append(name)
                    index = index + 1
    
            #주차장 소유
                    parking_area_posession.append(classifierPublic(name))
    
            #주차장 주소
                    path = "/html/body/div[3]/div[2]/div[1]/div[2]/div[2]/div[1]/div[2]/div[2]/ul/li["+k+"]/div[1]/dl/dd[1]"
                    addr = driver2.find_element_by_xpath(path)
                    addr = addr.text
                    print(addr)
                    parking_area_address.append(addr)
                
                except NoSuchElementException:
                    print("-"*10)
                    print("not found")
                    print("-"*10)
                    error_gu.append("indexError "+url)
        
                except IndexError:
                    print("-"*10)
                    print("IndexError")
                    print("-"*10)
                    error_gu.append("indexError "+url)
            for t in range(0, index):
                f.write(str(parking_area_name[t]) + "," + str(parking_area_posession[t]) + "," + str(parking_area_address[t]))
        time.sleep(4)

f.close()
driver2.close()