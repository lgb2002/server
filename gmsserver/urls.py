from django.contrib import admin
from django.conf.urls import url
from . import views

urlpatterns = [
    #url('',views.game_login,name='game_login'),
    url('download',views.download,name='download'),
    url('crolling',views.webCrolling,name='webCrolling'),
    url('fileRemove',views.fileRemove,name='fileRemove'),
    url('nowinfo',views.nowInfo,name='nowInfo'),
    #url('crollingstop',views.nowInfo,name='nowInfo'),
    #url('error',views.error,name='error'),
]