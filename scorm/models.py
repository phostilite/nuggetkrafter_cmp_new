from django.db import models
from clients.models import Client, ClientUser

class ScormAsset(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, blank=True)
    duration = models.DurationField(blank=True, null=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    scorm_id = models.IntegerField(unique=True, null=True)
    launch_url = models.URLField(blank=True, null=True)
    cover_photo = models.ImageField(upload_to="scorm_uploads/cover_photos/", blank=True, null=True, default="scorm_uploads/cover_photos/default.png")

    def __str__(self):
        return f"{self.title} - {self.scorm_id} - {self.id}"


class ScormResponse(models.Model):
    asset = models.OneToOneField(
        ScormAsset, on_delete=models.CASCADE, related_name="response"
    )
    status = models.BooleanField(null=True)
    message = models.TextField(null=True)
    scormdir = models.TextField(null=True)
    full_path_name = models.TextField(null=True)
    size = models.BigIntegerField(null=True)
    zippath = models.TextField(null=True)
    zipfilename = models.TextField(null=True)
    extension = models.CharField(max_length=10, null=True)
    filename = models.TextField(null=True)
    reference = models.TextField(null=True)
    scorm = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.asset.title


class ScormAssignment(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    scorm_asset = models.ForeignKey(ScormAsset, on_delete=models.CASCADE)
    date_assigned = models.DateTimeField(auto_now_add=True)
    number_of_seats = models.IntegerField(default=1)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    client_scorm_file = models.FileField(upload_to='client_scorm_files/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.client} - {self.scorm_asset}"
    
class Course(models.Model):
    title = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    cover_photo = models.URLField()
    short_description = models.CharField(max_length=250)
    long_description = models.TextField()
    scorm_assets = models.ManyToManyField(ScormAsset, blank=True)
    syncing_status = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class Module(models.Model):
    TYPE_CHOICES = [
        ('scorm', 'SCORM'),
    ]
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    file = models.URLField()

    def __str__(self):
        return self.title
    
class UserScormMapping(models.Model):
    user = models.ForeignKey(ClientUser, on_delete=models.CASCADE)
    assignment = models.ForeignKey(ScormAssignment, on_delete=models.CASCADE)
    launch_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.user} - {self.assignment}"

class UserScormStatus(models.Model):
    client_user = models.ForeignKey(ClientUser, on_delete=models.SET_NULL, null=True, blank=True)
    _scorm_id = models.CharField(max_length=255, blank=True, null=True)
    scorm_name = models.CharField(max_length=255, blank=True, null=True)
    complete_status = models.CharField(max_length=255, blank=True, null=True)
    satisfied_status = models.CharField(max_length=255, blank=True, null=True)
    total_time = models.CharField(max_length=255, blank=True, null=True)
    score = models.CharField(max_length=255, blank=True, null=True)
    attempt = models.IntegerField(default=1)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"UserScormStatus for {self.client_user} and {self.scorm_name}"
    
