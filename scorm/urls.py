from django.urls import path

from .views import get_all_scorms, download_scorm

urlpatterns = [
    path('get_all_scorms/', get_all_scorms, name='get_all_scorms'),
    path('download_scorm/<int:client_id>/<int:scorm_id>/', download_scorm, name='download_scorm'),
]
