from django.db import models
from django.utils import timezone
import datetime
from django.conf import settings

class UserInfo(models.Model):
	name = models.ForeignKey('auth.User',on_delete=models.CASCADE)

	def __str__(self):
		return str(self.name)

class CrollingData(models.Model):
    crolling_now = models.BooleanField(default = False)
    crolling_start = models.DateTimeField(auto_now = True)
    crolling_num = models.IntegerField(default=1)
    crolling_sum = models.IntegerField(default=1)

    now_code = models.TextField(max_length = 20, default="none")
    now_num = models.IntegerField(default=1)
    now_sum = models.IntegerField(default=1)
    def __str__(self):
        return " time: "+str(self.crolling_start) + "crolling_now : "+str(self.crolling_now)