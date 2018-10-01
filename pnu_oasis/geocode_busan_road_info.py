import os
import urllib.request
import urllib.error
import sys
import pandas as pd

busan_road_info_full_addr= pd.read_csv("C:\\Users\\han\\oasis\\csv\\busan_road_info_full_addr.csv", encoding='utf-8')

addr = list(busan_road_info_full_addr["full_addr"])
client_id = "eCXtGzVPh_MaKxU2eCdy"
client_secret = "BDILd1pMrz"

lon = []
lat = []
raw_data = []
for i in range(len(addr)):
    print(addr[i])
    encText = urllib.parse.quote(addr[i])
    
    url = "https://openapi.naver.com/v1/map/geocode?query=" + encText # json 결과
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id",client_id)
    request.add_header("X-Naver-Client-Secret",client_secret)
    
    try:
        response = urllib.request.urlopen(request)
        rescode = response.getcode()
        if(rescode==200):
            response_body = response.read()
            raw_data.append(response_body.decode('utf-8'))
            #print(response_body.decode('utf-8'))
            raw_data.append(response_body.decode('utf-8'))
            target_start_num = response_body.decode('utf-8').find('"부산광역시 ')
            #받아온 json 파일에 "부산광역시" 데이터면 위도/경도 추출
            if target_start_num >0:
                new_body = response_body.decode('utf-8')[target_start_num:]
                x_start_num = new_body.find('"x"')
                new_body = new_body[x_start_num:]
                x_end_num = new_body.find(',\n')
                x = new_body[5:x_end_num] #lon
                y_start_num = new_body.find('"y": ')
                new_body = new_body[y_start_num:]
                y_end_num = new_body.find("\n")
                y=new_body[5:y_end_num] #lat
                lon.append(x)
                lat.append(y)
            else:
                lon.append(0.0)
                lat.append(0.0)
        else:
            print("Error Code:" + rescode)
            raw_data.append(rescode)
    #검색이 안될 경우 위도경도는 0
    except urllib.error.HTTPError:
        print('can not find the url')
        print('null')
        lon.append(0.0)
        lat.append(0.0)

busan_road_info_full_addr["longitude"] = lon
busan_road_info_full_addr["latitude"] = lat
pd.DataFrame.to_csv(busan_road_info_full_addr,"C:\\Users\\han\\oasis\\csv\\busan_road_info_lonlat2.csv",sep=",",index=False)