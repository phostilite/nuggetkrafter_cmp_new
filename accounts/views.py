from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
import logging

from .forms import LoginForm

logger = logging.getLogger(__name__)

def landing_page(request):
    return redirect('login')

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    if user.is_superuser:
                        logger.info(f'Coreadmin {username} logged in')
                        return redirect('coreadmin_dashboard')
                    else:
                        if Group.objects.get(name='client') in user.groups.all():
                            logger.info(f'Client {username} logged in')
                            return redirect('client_dashboard')
                else:
                    messages.error(request, 'Inactive user')
            else:
                messages.error(request, 'Invalid username or password')
        else:
            messages.error(request, 'Invalid form data')
    else:
        form = LoginForm()
    return render(request, 'authentication/login.html', {'form': form})

def logout_view(request):
    username = request.user.username
    logout(request)
    logger.info(f'User {username} logged out')
    return redirect('login')