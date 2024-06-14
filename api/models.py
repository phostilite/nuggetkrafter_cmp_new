from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
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

class Notification(models.Model):
    message = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)