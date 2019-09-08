from django.shortcuts import render
from django.http import HttpResponse
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from google.auth import credentials
from apiclient import errors
from apiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload
#import mock
from wsgiref.util import FileWrapper
from django.views.decorators.csrf import csrf_exempt
import io, sys, csv, os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

creds = ""
try:
	import argparse
	flags = tools.argparser.parse_args([])
except ImportError:
	flags = None
SCOPES = 'https://www.googleapis.com/auth/drive.file'
print(os.getcwd())
print(BASE_DIR)
CLIENT_SECRET_FILE = os.getcwd()+'/gmsserver/client_secret.json'
CREDENTIAL_FILENAME = os.getcwd()+'/gmsserver/drive-python-upload.json'
store = file.Storage(CREDENTIAL_FILENAME)
creds = store.get()
if not creds or creds.invalid:
	print("make new storage data file ")
	flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
	creds = tools.run_flow(flow, store, flags)
DRIVE = build('drive', 'v3', http=creds.authorize(Http()))
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


def file_download(id, name):
	request = DRIVE.files().get_media(fileId=id)
	f = open(os.getcwd()+"/download/"+name,'wb')
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
		date = request.POST.get('date')
		code = request.POST.get('code')
		name = date+"-"+code+"c"
		print(name)
		file_download(find_folder(name),name)
		t = open("download/"+name)
		response =HttpResponse(content_type="text/csv")
		response['Content-Disposition']='attachment; filename="gmsserver/download/"'+name
		return response
	return HttpResponse("Hello World!")