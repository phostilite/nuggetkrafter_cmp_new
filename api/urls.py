from django.urls import path

from .views import validate_and_launch, user_scorm_status, sync_courses, get_scorm_data, reset_user_scorm_status, stats_view

urlpatterns = [
    path('get_scorm_data/<int:client_id>/<int:scorm_id>/', get_scorm_data, name='get_scorm_data'),
    path('validate_and_launch/', validate_and_launch, name='validate_and_launch'),
    path('user_scorm_status/', user_scorm_status, name='user_scorm_status'),
    path('sync_courses/', sync_courses, name='sync_courses'),
    path('reset_user_scorm_status/', reset_user_scorm_status, name='reset_user_scorm_status'),
    
    path('stats/', stats_view, name='stats_view'),
]
