from django.db import models
from django.contrib.auth.models import User

from clients.models import Client, ClientUser
from scorm.models import ScormAsset, ScormAssignment


class Statistics(models.Model):
    clients = models.IntegerField(default=0)
    users = models.IntegerField(default=0)
    scorm_packages = models.IntegerField(default=0)
    assignments = models.IntegerField(default=0)
    resets = models.IntegerField(default=0)
    status_checks = models.IntegerField(default=0)


class Activity(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    activity_type = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.activity_type} - {self.timestamp}'


class Notification(models.Model):
    message = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.message} - {self.timestamp}'
