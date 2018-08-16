
# 네이버 지도 크롤러를 이용한 비정형화된 주소 정형화


```python
import os
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import time
```

부산의 각 구청에서 받은 2년간 주정차단속민원데이터를 취합한 csv import


```python
all_illegal_parking= pd.read_csv(os.getcwd()+'\\csv\\all_illegal_parking.csv')
```


```python
all_illegal_parking.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>date</th>
      <th>time</th>
      <th>si</th>
      <th>gun_gu</th>
      <th>origin_addr</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2017-01-02</td>
      <td>10:16</td>
      <td>부산광역시</td>
      <td>기장군</td>
      <td>기장읍 차성남로89번길</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2017-01-02</td>
      <td>10:19</td>
      <td>부산광역시</td>
      <td>기장군</td>
      <td>기장읍 차성동로51번길</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2017-01-02</td>
      <td>10:19</td>
      <td>부산광역시</td>
      <td>기장군</td>
      <td>기장읍 차성동로51번길</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2017-01-02</td>
      <td>10:20</td>
      <td>부산광역시</td>
      <td>기장군</td>
      <td>기장읍 차성동로45번길</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2017-01-02</td>
      <td>10:26</td>
      <td>부산광역시</td>
      <td>기장군</td>
      <td>기장읍 차성로344번길</td>
    </tr>
  </tbody>
</table>
</div>




```python
alter_addr_lst = list(all_illegal_parking["origin_addr"])
alter_addr_lst[1:10]
```




    ['기장읍 차성동로51번길',
     '기장읍 차성동로51번길',
     '기장읍 차성동로45번길',
     '기장읍 차성로344번길',
     '기장읍 차성동로116번길',
     '기장읍 차성남로89번길',
     '기장읍 차성동로',
     '기장읍 읍내로',
     '기장읍 읍내로']



패턴을 파악해봤을때, 주소의 끝 글자가 '부' / '부근' /'번' /'가' 등 들어가거나 '('이 포함되어있으면 검색이 누락됨 -> 변경 혹은제거 필요.


```python
for k  in range(6): #6번  반복해서 검색 방어  패턴들 제거
    for i in range(len(alter_addr_lst)):
        alter_addr_lst[i] = alter_addr_lst[i].strip()
        if alter_addr_lst[i][-1] == "부":
            #print(alter_addr_lst[i])
            alter_addr_lst[i] = alter_addr_lst[i][0:-1]
            #print(alter_addr_lst[i])
        elif alter_addr_lst[i][-2:] =="부근":
            #print(alter_addr_lst[i])
            alter_addr_lst[i] = alter_addr_lst[i][0:-2]
            #print(alter_addr_lst[i])
        elif alter_addr_lst[i][-1] =="번":
            #print(alter_addr_lst[i])
            alter_addr_lst[i] = alter_addr_lst[i]+"길"
            #print(alter_addr_lst[i])
        elif alter_addr_lst[i][-1] =="가":
            #print(alter_addr_lst[i])
            alter_addr_lst[i] = alter_addr_lst[i][0:-1] +"번길"
            #print(alter_addr_lst[i])
        elif alter_addr_lst[i].find('(') > -1:
            #print(alter_addr_lst[i])
            alter_addr_lst[i] = alter_addr_lst[i][0:alter_addr_lst[i].find('(')]
            alter_addr_lst[i] = alter_addr_lst[i].strip()
            #print(alter_addr_lst[i])
        else:
            pass;
```

차후 맵핑을 위한 orgin_alter_lst 생성


```python
origin_alter_lst =[]
for i in range(len(alter_addr_lst)):
    origin_alter_lst.append(all_illegal_parking["origin_addr"][i]+"!!!"+alter_addr_lst[i])
```

unique(origin_alter_lst) -> origin_alter_lst는 네이버 맵 크롤링을 쿼리를 위한 값이기 때문에, 반복되는 값이 있어서는 안됨.


```python
origin_alter_lst = set(origin_alter_lst)
origin_alter_lst = list(origin_alter_lst)
len(origin_alter_lst)
```




    7760



반복 값이 제거된 origin_alter_lst를 다시 원래 형태인(origin_addr / alter_addr)로 변경


```python
dicted_ori_addr_lst = []
dicted_alt_addr_lst = []
for i in range(len(origin_alter_lst)):
    dicted_ori_addr_lst.append(origin_alter_lst[i].split("!!!")[0])
    dicted_alt_addr_lst.append(origin_alter_lst[i].split("!!!")[1])
```


```python
len(dicted_alt_addr_lst)
```




    7760



사전화된 리스트 들로 pandas df 생성 및 export


```python
dicted_address = pd.DataFrame({"ori_addr_lst":dicted_ori_addr_lst,"alt_addr_lst":dicted_alt_addr_lst})
pd.DataFrame.to_csv(dicted_address,os.getcwd()+'\\csv\\dicted_addr_illegal_parking1.csv',sep=",",index=False)
```

크롤링 시작

만약, 검색 주소 내 '번길'이 포함되어 있으면 이미 지오코딩이 가능하므로 검색하지 않음


```python
def byungil(i, lst, addr):
    if '번길' in lst[i]:
        address = lst[i]
        print("-"*10)
        print("attempt : "+str(i))
        print("Don't need to search")
        print(address)
        print("-"*10)
        addr.append(address)
        return(addr)
    else:
        next;
```

url에 검색어를 추가하여 webdriver로 파싱.


```python
def search_addr(i,lst,front,rear,addr):
    #웹드라이버 실행필요
    query = lst[i].replace(" ","+")
    url = front + query + rear
    print("-"*10)
    print("attempt : "+str(i))
    print(url)
    driver.get(url)
    path ="/html/body/div[3]/div[2]/div[1]/div[2]/div[2]/div[1]/div[2]/div[2]/ul/li[1]/div[1]/dl/dd[1]"
    address = driver.find_element_by_xpath(path)
    address = address.text
    address = str(address)
    address.replace("지번","")
    print(address)
    print("-"*10)
    addr.append(address)  
    return(addr)
```

웹의 동적인 작업을 위한 웹드라이버 호출


```python
driver = webdriver.Firefox()
```

address_for_geo라는 geocoding을 위한 리스트 생성하여 정제된 주소를 Input함
만약, 기존 주소(dicted_alt_addr_lst)에 "번길"이 포함이 되어있다면, 그 주소 그대로를 address_for_geo에 input하고, 나머지의 기존주소는 네이버 검색 후, 도로명 주소를 address_for_geo에 input함.


```python
address_for_geo10 = []
front = 'https://map.naver.com/?query='
rear = '&type=SITE_1'

for i in range(len(dicted_alt_addr_lst)):
    time.sleep(0.8) #네이버의 IP차단을 대비한 timesleep
    if (i%50==0):
        #print("time sleep per 50 events")
        try:
            if "번길" in dicted_alt_addr_lst[i]:
                byungil(i, dicted_alt_addr_lst,address_for_geo10)
            else:
                search_addr(i,dicted_alt_addr_lst,front,rear,address_for_geo10)
    
    else:
         if "번길" in dicted_alt_addr_lst[i]:
                byungil(i, dicted_alt_addr_lst,address_for_geo10)
            else:
                search_addr(i,dicted_alt_addr_lst,front,rear,address_for_geo10)
            
                except NoSuchElementException:
                    #print("-"*10)
                    #print("not found")
                    #print("-"*10)
                    address_for_geo10.append("NULL")
        
                except IndexError:
                    #print("-"*10)
                    #print("IndexError")
                    #print("-"*10)
                    address_for_geo10.append(dicted_alt_addr_lst[i])
```

사전화된 기존 주소, 사전화된 변경 주소, 지오코드를 위한 주소 리스트를 pandas 라이브러리 DataFrame화 시킴


```python
final_illigal_addr = pd.DataFrame({"dicted_alter_addr_lst":dicted_alt_addr_lst, "dicted_ori_addr_lst":dicted_ori_addr_lst,"address_for_geo":address_for_geo})
```

DataFrame을 csv로 export


```python
pd.DataFrame.to_csv(final_illigal_addr,os.getcwd()+'\\csv\\fianl_illigal_addr.csv',sep=",",index=False)
```
