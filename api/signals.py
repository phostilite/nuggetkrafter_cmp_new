from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from clients.models import Client, ClientUser
from scorm.models import ScormAsset, ScormAssignment
from .models import Statistics


@receiver(post_save, sender=Client)
def increment_clients(sender, **kwargs):
    stats = Statistics.objects.get(id=1)
    stats.clients += 1
    stats.save()

@receiver(post_save, sender=ClientUser)
def increment_users(sender, **kwargs):
    stats = Statistics.objects.get(id=1)
    stats.users += 1
    stats.save()

@receiver(post_save, sender=ScormAsset)
def increment_scorm_packages(sender, **kwargs):
    stats = Statistics.objects.get(id=1)
    stats.scorm_packages += 1
    stats.save()

@receiver(post_save, sender=ScormAssignment)
def increment_assignments(sender, **kwargs):
    stats = Statistics.objects.get(id=1)
    stats.assignments += 1
    stats.save()