from django.shortcuts import render
from django.http import HttpResponse, FileResponse, JsonResponse
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from google.auth import credentials
from apiclient import errors
from apiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload
from wsgiref.util import FileWrapper
from django.views.decorators.csrf import csrf_exempt
import io, sys, csv, os, json, requests, re
import pandas as pd
from pandas import Series, DataFrame
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import UserInfo, CrollingData
from datetime import datetime
from ipware.ip import get_ip
from django.db import migrations, models

try:
	import argparse
	flags = tools.argparser.parse_args([])
except ImportError:
	flags = None
SCOPES = 'https://www.googleapis.com/auth/drive.file'

static_dir = os.getcwd()
if(os.getcwd()[-1]!="r"):
	static_dir += "/server"
print(static_dir+'/gmsserver')
CLIENT_SECRET_FILE = static_dir+'/gmsserver/client_secret.json'
CREDENTIAL_FILENAME = static_dir+'/gmsserver/drive-python-upload.json'
store = file.Storage(CREDENTIAL_FILENAME)
creds = store.get()

if not creds or creds.invalid:
	print("make new storage data file ")
	flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
	creds = tools.run_flow(flow, store, flags)
DRIVE = build('drive', 'v3', http=creds.authorize(Http()), cache_discovery=False)
	#구글 드라이브와 연동


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
#폴더 및 파일 찾기

path_dir = "https://www.pythonanywhere.com/user/kakao/files/home/kakao/server/gmsserver/download/"

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

def file_download(id, name):
	request = DRIVE.files().get_media(fileId=id)
	f = open(static_dir+"/gmsserver/download/"+name+".csv",'wb')
	wr = csv.writer(f)
	downloader = MediaIoBaseDownload(f, request)
	done = False
	while done is False:
		status, done = downloader.next_chunk()
		print("Download "+str(int(status.progress()*100))+"%.")
	f.close()

def infoCroller(baseUrl, date, headers, cookies):
    while(1):
        try:
            url = baseUrl+"name.php?date="+date
            print(url)
            res = requests.get(url, headers=headers, cookies=cookies, timeout=30)
            break
        except:
            print("error loop")
            continue
    name = res.text
    #name = name.replace("\n","*")
    name = name.replace("\t",",")
    name = name.replace(" ",",")
    #name = name.replace("*","\n")
    print(name)
    ns = "주문번호,종목이름,임시,거래량,거래대금,종가,기준가"
    ns = ns+"\n"+name
    f = open(static_dir+"/gmsserver/data/info.csv",'w', encoding='utf-8')
    f.write(ns)
    context = ""
    f = open(static_dir+"/gmsserver/data/info.csv",'r', encoding='utf-8')
    while True:
        line = f.readline()
        if not line:
            break
        if line.count(',') == 6:
            context += line
    f = open(static_dir+"/gmsserver/data/info.csv",'w+t', encoding='utf-8')
    f.write(context)
    f.close()
    infopd = pd.read_csv(static_dir+"/gmsserver/data/info.csv")
    #code = str(infopd["주문번호"][1])
    #print (code)
    return infopd

def contractCroller(baseUrl,date,code,headers,cookies):
    while(1):
        try:
            url = baseUrl+"contract.php?d="+date+"&c="+code
            print("url:"+url)
            res = requests.get(url, headers=headers, cookies=cookies, timeout=80)
            break
        except:
            print("error loop")
            continue
    contract = res.text
    #if(contract==""):
    #    print("contract"+date+": none")
    #    continue
    print("contract"+date+": done")
    #체결 내역을 보여줌
    #f = open(static_dir+"/gmsserver/data/"+date+"-"+code+"c.csv",'w', encoding='utf-8')
    f = open(static_dir+"/gmsserver/data/contract.csv",'w', encoding='utf-8')
    f.write(contract)
    f.close()

def hogaCroller(baseUrl,date,code,headers,cookies,type):
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
    if type==1 :
        url = baseUrl+"first.php?date="+date+"&code="+code+"&time=90000000"
        res = requests.get(url, headers=headers, cookies=cookies, timeout=800)
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
        try:
            for list in text:
                sp = list.split(',')
                if(list[2]=="1"):data1+=list+",,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n"
                elif(list[2]=="2"):data2+=','.join(sp[:6])+",,,,,,,,,,,,,"+','.join(sp[6:])+"\n"
                elif(list[2]=="3"):data3+=list+"\n"
                elif(list[2]=="4"):data4+=list+"\n"
            no = text[-1].split(',')[3]
            #print(no)
        except:
            hogaCroller(baseUrl,date,code,headers,cookies,1)
        while(1):
            url = baseUrl+"next.php?date="+date+"&code="+code+"&no="+no
            while(1):
                try:
                    res = requests.get(url, headers=headers, cookies=cookies)
                    break
                except:
                    print("error loop")
                    continue
            string = res.text
            if(string==""):
                print("end!")
                break
            string = string.replace("\n","*")
            string = string.replace("\t",",")
            string = string.replace(",*","\n")
            string = string[:-1]
            text = re.split('[\n]', string)
            try:
                for list in text:
                    sp = list.split(',')
                    if(list[0]=="1"):data1+="2,"+list+",,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n"
                    elif(list[0]=="2"):data2+="2,"+','.join(sp[:5])+",,,,,,,,,,,,,"+','.join(sp[5:])+"\n"
                    elif(list[0]=="3"):data3+="2,"+list+"\n"
                    elif(list[0]=="4"):data4+="2,"+list+"\n"
                no = text[-1].split(',')[2]
            except:
                print("what error?"+ str(ex))
                print(url)
                hogaCroller(url,date,code,headers,cookies,2)
        data = column + data1 + data2
        f = open(static_dir+"/gmsserver/data/data.csv",'w', encoding='utf-8')
        f.write(data)
        f.close()
    elif type==2 : #error 발생으로 다시 반복할 경우 type = 2가 된다.
        print("type 2")
        while(1):
            try:
                res = requests.get(url, headers=headers, cookies=cookies)
                string = res.text
                if(string==""):
                    print("end!")
                    break
                string = string.replace("\n","*")
                string = string.replace("\t",",")
                string = string.replace(",*","\n")
                string = string[:-1]
                text = re.split('[\n]', string)
                try:
                    for list in text:
                        sp = list.split(',')
                        if(list[0]=="1"):data1+="2,"+list+",,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n"
                        elif(list[0]=="2"):data2+="2,"+','.join(sp[:5])+",,,,,,,,,,,,,"+','.join(sp[5:])+"\n"
                        elif(list[0]=="3"):data3+="2,"+list+"\n"
                        elif(list[0]=="4"):data4+="2,"+list+"\n"
                    no = text[-1].split(',')[2]
                except:
                    print(list)
            except Exception as ex: # 에러 종류
                print("what error?"+ str(ex))
                print(list)
                print(sp)
                print(url)
                hogaCroller(url,date,code,headers,cookies,2)
        data = column + data1 + data2
        f = open(static_dir+"/gmsserver/data/data.csv",'w', encoding='utf-8')
        f.write(data)
        f.close()


def codeCroller(baseUrl,date,code,headers,cookies,type):
    fileRemove(1)
    print(code)
    contractCroller(baseUrl,date,code,headers,cookies)
    hogaCroller(baseUrl,date,code,headers,cookies,type)

    #upload(date+"-"+code+"h","None",static_dir+"/gmsserver/data/data.csv")
    #upload(date+"-"+code+"c","None",static_dir+"/gmsserver/data/contract.csv")


def test(time,num):
    date = str(time)
    baseUrl = "http://hogaplay.com/player/"
    headers = {'Accept': '*/*','Accept-Encoding': 'gzip, deflate','Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7','Referer': 'http://hogaplay.com/player/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36','X-Requested-With': 'XMLHttpRequest'}
    cookies = {'k': '1dzYvlOyvbZA62v4pmI3WlPZObOsV7dH7kBVIov173qxox', 'n': 'vlogi'}

    try:
    	#print("1")
    	if os.path.isfile(static_dir+"/gmsserver/data/info.csv"):
    		os.remove(static_dir+"/gmsserver/data/info.csv")

    	codeList = infoCroller(baseUrl, date, headers, cookies)
    	#print("2")
    	#자료 구조는 pandas:pd이다.
    	if CrollingData.objects.all()[0].crolling_now == False:
    		return 0
    	cd = CrollingData.objects.get(crolling_now = True)
    	cd.now_sum = len(codeList["주문번호"])
    	cd.save()
    	#print("3")
    	for i in range(num,len(codeList["주문번호"])):
            try:
            	print(str(i))
            	#print("4")
            	if CrollingData.objects.all()[0].crolling_now == False:
            		break
            	cd = CrollingData.objects.get(crolling_now = True)
            	cd.now_num = i
            	code = codeList["주문번호"][i]
            	cd.now_code = code
            	cd.save()
            	#print("5")
            	codeCroller(baseUrl,date,code,headers,cookies,1)
            	#print("6")
            except Exception as ex: # 에러 종류
            	#print("5")
            	print("error in nextCroller()"+ str(ex)) # ex는 발생한 에러의 이름을 받아오는 변수
            	print("i : "+str(i))
            	test(date,i)
            	return("error in nextCroller()"+ str(ex))
        #upload(date+"-i","None",static_dir+"/gmsserver/data/info.csv")
        #return ("All done!")
    except Exception as ex: # 에러 종류
        print("error in infoCroller()"+ str(ex)) # ex는 발생한 에러의 이름을 받아오는 변수
        return("error in infoCroller()"+ str(ex))

def fileRemove(meaningless):
    if os.path.isfile(static_dir+"/gmsserver/data/contract.csv"):
        os.remove(static_dir+"/gmsserver/data/contract.csv")
    if os.path.isfile(static_dir+"/gmsserver/data/data1.csv"):
        os.remove(static_dir+"/gmsserver/data/data1.csv")
    if os.path.isfile(static_dir+"/gmsserver/data/data2.csv"):
        os.remove(static_dir+"/gmsserver/data/data2.csv")
    if os.path.isfile(static_dir+"/gmsserver/data/data.csv"):
        os.remove(static_dir+"/gmsserver/data/data.csv")
    if meaningless != 1:
    	return render(meaningless, 'gmsserver/index.html', {'result':'remove success'})


@csrf_exempt
def download(request):
	'''
	if os.path.isfile("gmsserver/download/"+name):
	os.remove("gmsserver/download/"+name)
	'''
	if request.method == "POST":
		data = json.loads(request.body)
		name = data['name']
		code = data['code']
		date = data['date']
		print(str(name)+":"+str(date)+"/"+str(code))
		#json need to be used json.loads syntax
  		#date=request.POST.get('date')
		#code=request.POST.get('code')
		#name=request.POST.get('name')
		#print(str(name)+":"+str(date)+"/"+str(code))
		#print(request.text)
		#date = "20181119"
		#code = "257370"
		name = str(date)+"-"+str(code)+"c"
		#print(name)
		file_download(find_folder(name),name)
		file_path = static_dir+"/gmsserver/download/"+name+".csv"
		response = FileResponse(open(file_path, 'rb'))
		response['Content-Type'] = 'application/octet-stream'
		response['Content-Disposition'] = 'attachment;filename="{0}"'.format(os.path.basename(file_path))
		response['Content-Length'] = os.path.getsize(file_path)
		return response
		'''
		with open(static_dir+"/gmsserver/download/"+name+".csv",'r') as t:
			file_data = t.read()
		#response =HttpResponse(file_data, content_type="text/csv")
		#response['Content-Disposition']='attachment; filename=name'
		#print("file response")
		length = len(file_data)
		data = file_data[30:20000]
		data = data.replace("\"","")
		data = data.replace(",","")
		data = data.replace(":","")
		data = data.replace("\n","")
		data = data.replace("\t","")
		data = data.replace("+","")
		data = data.replace("-","")
		data = data.replace(" ","")
		data = data.replace("'","")
		#data = "'"+data+"'"
		#length = len(data)
		data = "length/"+str(length)+"/"+data
		length2 = len(data)
		print(length2)
		#return HttpResponse("helooooo")
		#return response
		#response_data = {}
		#response_data['data'] = data
		#return HttpResponse(json.dumps(response_data), content_type="application/json")
		return HttpResponse(data)
		'''
	elif request.method == "GET":
		date = "20181119"
		code = "257370"
		name = str(date)+"-"+str(code)+"h"
		file_download(find_folder(name),name)
		file_path = static_dir+"/gmsserver/download/"+name+".csv"
		response = FileResponse(open(file_path, 'rb'))
		response['Content-Type'] = 'application/octet-stream'
		#text/csv
		#application/vnd.ms-excel
		response['Content-Disposition'] = 'attachment;filename="{0}"'.format(os.path.basename(file_path))
		response['Content-Length'] = os.path.getsize(file_path)
		return response

@csrf_exempt
def webCrolling(request):
	if (ipCheck(request)):
		if request.method == "GET":
			return render(request, 'gmsserver/index.html')
		elif request.method == "POST":
			date=request.POST.get('dateRequest')
			date = date.replace(" ","")
			date = date.split(',')
			if len(CrollingData.objects.all()) >= 1:
				cd = CrollingData.objects.all()
				cd.delete()
			if len(CrollingData.objects.all()) == 0:
				cd = CrollingData(
					crolling_now = True,
					crolling_start = datetime.now(),
					crolling_sum = len(date),
					crolling_num = 0
				)
				cd.save()

				for day in date:
					print(day)
					test(day,0)
					if CrollingData.objects.all()[0].crolling_now == False:
						break
					cd = CrollingData.objects.get(crolling_now = True)
					cd.crolling_num+=1
					cd.save()
				return render(request, 'gmsserver/index.html', {'date':date, 'sum':len(date)})
	else:
		print("hello")
		return render(request, 'gmsserver/error.html')


@csrf_exempt
def nowInfo(request):
	if request.POST.get('stopCrolling') == "stop crolling":
		print("stop crolling")
		if CrollingData.objects.all()[0].crolling_now :
			cd = CrollingData.objects.get(crolling_now = True)
			cd.crolling_now = False
			cd.save()
			print("crolling --stop")
		else:
			print("no crolling")
	try:
		cd = CrollingData.objects.get(crolling_now = True)
		return render(request, 'gmsserver/nowinfo.html', {
			'crolling_now':cd.crolling_now,
			'crolling_num':cd.crolling_num,
			'crolling_sum':cd.crolling_sum,
			'crolling_start':cd.crolling_start,
			'now_num':cd.now_num,
			'now_sum':cd.now_sum,
			'now_code':cd.now_code,
		})
	except:
		return render(request, 'gmsserver/nowinfo.html')

		
def ipCheck(request):
	ip = get_ip(request)
	print(ip)
	if(ip=="127.0.0.1"):
		return 1
	else:
		return 0