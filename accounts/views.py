from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from datetime import datetime
import logging

from .forms import LoginForm
from api.models import Activity

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
                    activity = Activity.objects.create(
                        user=user,
                        activity_type='logged in',
                        timestamp=datetime.now()
                    )
                    activity.save()
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
    activity = Activity.objects.create(
        user=request.user,
        activity_type='logged out',
        timestamp=datetime.now()
    )
    activity.save()
    logout(request)
    logger.info(f'User {username} logged out')
    return redirect('login')

