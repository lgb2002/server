import os,sys,io,requests,openpyxl,xlrd,xlwt,csv,re
import pandas as pd
from pandas import Series, DataFrame
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from google.auth import credentials
from apiclient import errors
from apiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, QtCore
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding = 'utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding = 'utf-8')
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
def upload(name, parent_id, file):
    media_body = MediaFileUpload(file, mimetype='text/csv', resumable=True)
    body = {'name': name,'mimeType': 'text/csv'}
    if parent_id: body['parents'] = [{'id': parent_id}]
    file = DRIVE.files().create(body=body,media_body=media_body).execute()
def create_folder(name):
    file_metadata = {'name': name,'mimeType': 'application/vnd.google-apps.folder'}
    file = DRIVE.files().create(body=file_metadata,fields='id').execute()
    print('Folder ID: %s' % file.get('id'))
def find_folder(name):
    page_token = None
    while True:
        response = DRIVE.files().list(q="name='"+name+"'",pageToken=page_token).execute()
        for file in response.get('files', []):
            print ('Found file: %s (%s)' % (file.get('name'), file.get('id')))
            return (file.get('id'))
        page_token = response.get('nextPageToken', None)
        if page_token is None:break
def create_folder_indoor(name, folder_id):
    file_metadata = {'name': name,'mimeType': 'application/vnd.google-apps.folder','parents': [folder_id]}
    file = DRIVE.files().create(body=file_metadata,fields='id').execute()
def create_file_indoor(name, folder_id):
    file_metadata = {'name': name,'mimeType': 'text/txt','parents': [folder_id]}
    file = DRIVE.files().create(body=file_metadata,fields='id').execute()
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
