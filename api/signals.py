from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from clients.models import Client, ClientUser
from scorm.models import ScormAsset, ScormAssignment
from .models import Statistics
