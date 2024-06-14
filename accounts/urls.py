from django.urls import path

from .views import login_view, logout_view, landing_page

urlpatterns = [
    path('', landing_page, name='landing_page'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
]
