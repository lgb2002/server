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
import io, sys, csv, os, json

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

@csrf_exempt
def hello_world(request):
	'''
	if os.path.isfile("gmsserver/download/"+name):
	os.remove("gmsserver/download/"+name)
	'''
	if request.method == "POST":
		date = "20181119"
		code = "257370"
		name = str(date)+"-"+str(code)+"c"
		#print(name)
		file_download(find_folder(name),name)
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