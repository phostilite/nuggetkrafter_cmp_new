from django.urls import path

from . import views

urlpatterns = [
    path('get_scorm_data/<int:client_id>/<int:scorm_id>/', views.get_scorm_data, name='get_scorm_data'),
    path('validate_and_launch/', views.validate_and_launch, name='validate_and_launch'),
    path('user_scorm_status/', views.user_scorm_status, name='user_scorm_status'),
    path('sync_courses/', views.sync_courses, name='sync_courses'),
    path('reset_user_scorm_status/', views.reset_user_scorm_status, name='reset_user_scorm_status'),
    
    path('stats/', views.stats_view, name='stats_view'),
    path('activities/', views.activities_view, name='activities_view'),
    path('client_users/', views.fetch_client_users, name='fetch_client_users'),
    path('clients/', views.fetch_clients, name='fetch_clients'),

    path('check_username/<str:username>', views.check_username, name='check_username'),

    path('user_scorm_status_json/<int:user_scorm_status_id>/', views.fetch_user_scorm_status, name='user_scorm_status'),
    path('fetch_user_scorm_status_chart_data/<int:user_scorm_status_id>/', views.fetch_user_scorm_status_chart_data, name='fetch_user_scorm_status_chart_data'),
    path('fetch_user_scorm_kpi_data/<int:user_scorm_status_id>/', views.fetch_user_scorm_kpi_data, name='fetch_user_scorm_kpi_data'),
]
