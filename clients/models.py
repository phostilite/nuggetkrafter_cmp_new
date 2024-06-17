from django.db import models
from django.contrib.auth.models import User
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField()
    contact_phone = models.CharField(max_length=20, null=True, blank=True)
    company = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    domains = models.TextField(blank=True, null=True)
    lms_url = models.URLField(blank=True, null=True)
    lms_api_key = models.CharField(max_length=100, blank=True, null=True)
    lms_api_secret = models.CharField(max_length=100, blank=True, null=True)

    def scorm_count(self):
        cache_key = f'scorm_count_{self.pk}'
        count = cache.get(cache_key)
        if count is None:
            count = self.scormassignment_set.count()
            cache.set(cache_key, count, 3600)
        return count

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class ClientUser(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    scorm_consumed = models.IntegerField(default=0)
    learner_id = models.CharField(max_length=255)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    cloudscorm_user_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def update_scorm_consumed(self):
        from scorm.models import UserScormMapping

        count = UserScormMapping.objects.filter(user=self).count()
        logger.info(f"Updating scorm consumed for {self} to {count}")
        self.scorm_consumed = count
        self.save()

        return count

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
