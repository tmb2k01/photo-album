import datetime

from django.contrib.auth.models import User
from django.db import models


class Photo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to="photos/")
    name = models.CharField(max_length=255)
    upload_date = models.DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return self.name
