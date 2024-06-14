from django.urls import path

from .views import dashboard, client_list, client_profile, client_user_list, manage_scorm, assign_scorm, scorm_iframe, get_client_details, client_update_view, get_user_details, user_update_view, scorm_list

urlpatterns = [
    path('dashboard/', dashboard, name='coreadmin_dashboard'),

    path('scorm/', scorm_list, name='scorm_list'),
    path('scorm/<int:scorm_id>/', scorm_iframe, name='scorm_iframe'),

    path('clients/', client_list, name='client_list'),
    path('clients/<int:client_id>/', client_profile, name='client_profile'),
    path('clients/<int:client_id>/users/', client_user_list, name='client_user_list'),
    path('clients/<int:client_id>/scorm/', manage_scorm, name='manage_scorm'),
    path('clients/<int:client_id>/scorm/assign/', assign_scorm, name='assign_scorm'),
    path('clients/<int:client_id>/details/', get_client_details, name='get_client_details'),
    path('clients/<int:client_id>/update/', client_update_view, name='client_update_view'),
    path('clients/<int:client_id>/users/<int:user_id>/details/', get_user_details, name='get_user_details'),
    path('clients/<int:client_id>/users/<int:user_id>/update/', user_update_view, name='user_update_view'),

    
]
