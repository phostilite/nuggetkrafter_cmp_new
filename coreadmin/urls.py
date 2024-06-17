from django.urls import path

from . import views
from scorm.views import ScormUploadView

urlpatterns = [
    path('dashboard/', views.dashboard, name='coreadmin_dashboard'),

    path('scorm/', views.scorm_list, name='scorm_list'),
    path('scorm/<int:scorm_id>/', views.scorm_iframe, name='scorm_iframe'),
    path('scorm/upload/', ScormUploadView.as_view(), name='scorm_upload'),
    path('scorm/<int:scorm_id>/details/', views.get_scorm_details, name='get_scorm_details'),
    path('scorm/<int:scorm_id>/update/', views.scorm_update_view, name='scorm_update_view'),

    path('clients/', views.client_list, name='client_list'),
    path('clients/create/', views.create_client, name='create_client'),
    path('clients/<int:client_id>/', views.client_profile, name='client_profile'),
    path('clients/<int:client_id>/scorm/', views.manage_scorm, name='manage_scorm'),
    path('clients/<int:client_id>/scorm/assign/', views.assign_scorm, name='assign_scorm'),
    path('clients/<int:client_id>/details/', views.get_client_details, name='get_client_details'),
    path('clients/<int:client_id>/update/', views.client_update_view, name='client_update_view'),

    path('clients/<int:client_id>/users/', views.client_user_list, name='client_user_list'),
    path('clients/<int:client_id>/users/<int:user_id>/details/', views.get_user_details, name='get_user_details'),
    path('clients/<int:client_id>/users/<int:user_id>/update/', views.user_update_view, name='user_update_view'),
    path('clients/<int:client_id>/users/<int:user_id>/profile/', views.client_user_profile, name='user_profile'),
    path('clients/<int:client_id>/users/<int:user_id>/scorm/', views.client_user_mapped_scorm, name='client_user_mapped_scorm'),
    path('clients/<int:client_id>/users/<int:user_id>/scorm/<int:scorm_id>/progress/', views.client_user_mapped_scorm_progress, name='client_user_mapped_scorm_progress'),


]
