import os
import sys
import io
import requests
import pandas as pd
from pandas import Series, DataFrame
import openpyxl
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from google.auth import credentials
from apiclient import errors
from apiclient.http import MediaFileUpload
import xlrd
import xlwt
import csv
import re
from googleapiclient.http import MediaIoBaseDownload
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, QtCore

sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding = 'utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding = 'utf-8')
#한글 출력

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None
SCOPES = 'https://www.googleapis.com/auth/drive.file'
CLIENT_SECRET_FILE = 'client_secret.json'
CREDENTIAL_FILENAME = 'drive-python-upload.json'
store = file.Storage(CREDENTIAL_FILENAME)
creds = store.get()
if not creds or creds.invalid:
    print("make new storage data file ")
    flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
    creds = tools.run_flow(flow, store, flags)
DRIVE = build('drive', 'v3', http=creds.authorize(Http()))
#구글 드라이브와 연동
i=0

def upload(name, parent_id, file):
    media_body = MediaFileUpload(file, mimetype='text/csv', resumable=True)
    body = {
        'name': name,
        'mimeType': 'text/csv'
    }
    if parent_id:
        body['parents'] = [{'id': parent_id}]
    file = DRIVE.files().create(body=body,media_body=media_body).execute()
#ex) upload(C:/Users/lgb/tf_auto_stock/test.txt','test222')
#업로드 함수

def create_folder(name):
    file_metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    file = DRIVE.files().create(body=file_metadata,fields='id').execute()
    print('Folder ID: %s' % file.get('id'))
#폴더 생성 함수

def find_folder(name):
    page_token = None
    while True:
        response = DRIVE.files().list(q="name='"+name+"'",
                                              pageToken=page_token).execute()
        for file in response.get('files', []):
            # Process change
            print ('Found file: %s (%s)' % (file.get('name'), file.get('id')))
            return (file.get('id'))
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
        #무슨 용도의 코드인지 이해 불
#폴더 및 파일 찾기 함수

def create_folder_indoor(name, folder_id):
    file_metadata = {
    'name': name,
    'mimeType': 'application/vnd.google-apps.folder',
    'parents': [folder_id]
    }
    file = DRIVE.files().create(body=file_metadata,fields='id').execute()
#폴더 내부에 폴더 만드는 함수

def create_file_indoor(name, folder_id):
    file_metadata = {
    'name': name,
    'mimeType': 'text/txt',
    'parents': [folder_id]
    }
    file = DRIVE.files().create(body=file_metadata,fields='id').execute()
#폴더 내부에 파일 저장하는 함수

def file_download(id,name):
    request = DRIVE.files().get_media(fileId=id)
    f = open("download/"+name+".csv",'wb')
    wr = csv.writer(f)
    downloader = MediaIoBaseDownload(f, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print ("Download " + str(int(status.progress() * 100))+"%.")
        f.close()


def fileRemove():
    if os.path.isfile("data/contract.csv"):
        os.remove("data/contract.csv")
    if os.path.isfile("data/data1.csv"):
        os.remove("data/data1.csv")
    if os.path.isfile("data/data2.csv"):
        os.remove("data/data2.csv")
    if os.path.isfile("data/data.csv"):
        os.remove("data/data.csv")

def infoCroller(baseUrl, date, headers, cookies):
    url = baseUrl+"name.php?date="+date
    res = requests.get(url, headers=headers, cookies=cookies, timeout=10)
    name = res.text
    #name = name.replace("\n","*")
    name = name.replace("\t",",")
    name = name.replace(" ",",")
    #name = name.replace("*","\n")
    ns = "주문번호,종목이름,임시,거래량,거래대금,종가,기준가"
    ns = ns+"\n"+name
    f = open("data/info.csv",'w', encoding='utf-8')
    f.write(ns)
    context = ""
    f = open("data/info.csv",'r', encoding='utf-8')
    while True:
        line = f.readline()
        if not line:
            break
        if line.count(',') == 6:
            context += line
    f = open("data/info.csv",'w+t', encoding='utf-8')
    f.write(context)
    f.close()
    infopd = pd.read_csv("data/info.csv")

    #code = str(infopd["주문번호"][1])
    #print (code)
    return infopd

def contractCroller(baseUrl,date,code,headers,cookies):
    url = baseUrl+"contract.php?d="+date+"&c="+code
    print("url:"+url)
    res = requests.get(url, headers=headers, cookies=cookies, timeout=10)
    contract = res.text
    #if(contract==""):
    #    print("contract"+date+": none")
    #    continue
    print("contract"+date+": done")
    #체결 내역을 보여줌
    #f = open("data/"+date+"-"+code+"c.csv",'w', encoding='utf-8')
    f = open("data/contract.csv",'w', encoding='utf-8')
    f.write(contract)
    f.close()

def hogaCroller(baseUrl,date,code,headers,cookies):
    column = "장전중후,매매유형,번호1,번호2,실제시간,가상시간,등락,등락률,호가변화량,거래량,거래대금,시가,고가,저가,전일거,전일비거,회전율,\
    전일비체결강도,도1가,도2가,도3가,도4가,도5가,도6가,도7가,도8가,도9가,도10가,도1거,도2거,도3거,도4거,도5거,도6거,도7거,도8거,도9거,도10거,\
    도1체,도2체,도3체,도4체,도5체,도6체,도7체,도8체,도9체,도10체,수1가,수2가,수3가,수4가,수5가,수6가,수7가,수8가,수9가,수10가,\
    수1거,수2거,수3거,수4거,수5거,수6거,수7거,수8거,수9거,수10거,수1체,수2체,수3체,수4체,수5체,수6체,수7체,수8체,수9체,수10체,\
    매도거래량,매도거래변화량,매수거래량,매수거래변화량\n"
    #파일 column 설정 (csv 파일 저장 순서는 data1 -> data2 -> data3 -> data4 -> default -> others)
    #원래 순서는 data2부터였다. 왜냐하면 호가창이 더 중요하기 때문이다. 그러나 호가창은 컬럼이 너무 많아 data1부터 하는 게 csv가 예쁠 것 같다.
    #* data3과 data4는 사용 방법을 잘 모르겠음, 생략
    #data1 : 호가창 변화량을 보여줌
    #data2 : 호가창 배열을 보여줌
    #data3 : 잘 모르겠음
    #data4 : 기관, 외국인 거래내역을 보여줌

    url = baseUrl+"first.php?date="+date+"&code="+code+"&time=90000000"
    print("url:"+url)
    res = requests.get(url, headers=headers, cookies=cookies, timeout=10)
    string = res.text
    #if(string==""):
    #    print("string"+number+": none")
    #    continue
    print("date:"+date+"\ncode:"+code)
    #호가창을 보여줌
    #print(url)
    #print(string)
    string = string.replace("\n","*")
    string = string.replace("\t",",")
    string = string.replace(",*","\n")
    #string = "장전중후,매매유형,번호1,번호2,실제시간,가상시간\n"+string
    string = string[:-1]
    #다운받은 문자열을 csv 파일 형태로 변환 (값 사이에 ',' 넣음)
    #first.php에서 받아온 첫번째 파일
    #sentences = re.split(r['*'],string)
    text = re.split('[\n]', string)
    #print(part[0])
    #print(string)
    data1=""
    data2=""
    data3=""
    data4=""
    default=""
    for list in text:
        sp = list.split(',')
        if(list[2]=="1"):data1+=list+",,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n"
        elif(list[2]=="2"):data2+=','.join(sp[:6])+",,,,,,,,,,,,,"+','.join(sp[6:])+"\n"
        elif(list[2]=="3"):data3+=list+"\n"
        elif(list[2]=="4"):data4+=list+"\n"
        #else:default+=list+"\n"
        #print("data:"+data3)
    no = text[-1].split(',')[3]
    #print(no)
    #first.php?
    while(1):#res.text != ""):
        url = baseUrl+"next.php?date="+date+"&code="+code+"&no="+no
        res = requests.get(url, headers=headers, cookies=cookies, timeout=10)
        string = res.text
        if(string==""):
            print("end!")
            break
        #if(res.text == ""):
        #    break;
        string = string.replace("\n","*")
        string = string.replace("\t",",")
        string = string.replace(",*","\n")
        string = string[:-1]
        text = re.split('[\n]', string)
        for list in text:
            sp = list.split(',')
            if(list[0]=="1"):data1+="2,"+list+",,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n"
            elif(list[0]=="2"):data2+="2,"+','.join(sp[:5])+",,,,,,,,,,,,,"+','.join(sp[5:])+"\n"
            elif(list[0]=="3"):data3+="2,"+list+"\n"
            elif(list[0]=="4"):data4+="2,"+list+"\n"
            #else:default+="2,"+list+"\n"
        no = text[-1].split(',')[2]
        #print(data1)
        #print(data2)
        #print(no)
        #next.php?
    data = column + data1 + data2
    #f = open("data/"+date+"-"+code+"h.csv",'w', encoding='utf-8')
    f = open("data/data.csv",'w', encoding='utf-8')
    f.write(data)
    f.close()
    #f = open("data/data2.csv",'w', encoding='utf-8')
    #f.write(data2)
    #f.close()
    #f = open("data/data3.csv",'w', encoding='utf-8')
    #f.write(data3)
    #f.close()
    #f = open("data/data4.csv",'w', encoding='utf-8')
    #f.write(data4)
    #f.close()
    #csv 파일 형태로 저장
    #df = pd.read_csv("data/type1.csv")
    #print(df.shape)
    #print(df["매매유형"][0])
    #res = requests.get(baseUrl+"next.php?date="+datetime['dateList'][0]+"&code="+list['종목코드'][0]+"&no="+no, headers=headers, cookies=cookies)
    #string = res.text
    #next.php에서 받아온 이후의 파일
    #return data

baseUrl = "http://hogaplay.com/player/"
headers = {'Accept': '*/*','Accept-Encoding': 'gzip, deflate','Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7','Referer': 'http://hogaplay.com/player/',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36','X-Requested-With': 'XMLHttpRequest'}
cookies = {'k': '1dzYvlOyvbZA62v4pmI3WlPZObOsV7dH7kBVIov173qxox', 'n': 'vlogi'}
infoCroller(baseUrl, "20191017", headers, cookies)

def test(time,num):
    date = str(time)
    baseUrl = "http://hogaplay.com/player/"
    headers = {'Accept': '*/*','Accept-Encoding': 'gzip, deflate','Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7','Referer': 'http://hogaplay.com/player/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36','X-Requested-With': 'XMLHttpRequest'}
    cookies = {'k': '1dzYvlOyvbZA62v4pmI3WlPZObOsV7dH7kBVIov173qxox', 'n': 'vlogi'}

    if os.path.isfile("data/info.csv"):
        os.remove("data/info.csv")
    codeList = infoCroller(baseUrl, date, headers, cookies)
    upload(date+"-i","None","data/info.csv")
    #자료 구조는 pandas:pd이다.
    for i in range(num,len(codeList["주문번호"])):
        try:
            code = codeList["주문번호"][i]
            fileRemove()
            print(code)
            contractCroller(baseUrl,date,code,headers,cookies)
            hogaCroller(baseUrl,date,code,headers,cookies)

            upload(date+"-"+code+"h","None","data/data.csv")
            upload(date+"-"+code+"c","None","data/contract.csv")
        except:
            print("i : "+str(i))
    #return ("All done!")

#test("20191017",0)
