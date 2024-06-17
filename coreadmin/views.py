import logging
import traceback

from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from datetime import datetime, timedelta

from coreadmin.utils import str_to_seconds
from scorm.models import ScormAsset, ScormAssignment, ScormResponse, UserScormMapping, UserScormStatus
from clients.models import Client, ClientUser
from scorm.forms import AssignSCORMForm, ScormUpdateForm
from clients.forms import ClientUpdateForm, UserUpdateForm, ClientForm
from api.models import Activity, Notification

logger = logging.getLogger(__name__)


def dashboard(request):
    return render(request, 'coreadmin/dashboard.html')


def scorm_list(request):
    try:
        scorm_assets = ScormAsset.objects.all()
    except ObjectDoesNotExist:
        messages.error(request, "Error fetching SCORM assets")
        scorm_assets = None
    return render(request, 'coreadmin/scorm_list.html', {'scorm_assets': scorm_assets})


def client_list(request):
    try:
        clients = Client.objects.all()
    except ObjectDoesNotExist:
        messages.error(request, "Error fetching clients")
        clients = None
    return render(request, 'coreadmin/client_list.html', {'clients': clients})


def client_profile(request, client_id):
    try:
        client = Client.objects.get(id=client_id)
    except ObjectDoesNotExist:
        messages.error(request, "Error fetching client")
        client = None
    return render(request, 'coreadmin/client_profile.html', {'client': client})


def client_user_list(request, client_id):
    try:
        client = Client.objects.get(id=client_id)
        client_users = ClientUser.objects.filter(client=client)

        for user in client_users:
            user.update_scorm_consumed()
    except ObjectDoesNotExist:
        messages.error(request, "Error fetching client users")
        client_users = None
    return render(request, 'coreadmin/client_user_list.html', {'client_users': client_users, 'client': client})


def manage_scorm(request, client_id):
    try:
        scorm_assignments = ScormAssignment.objects.filter(client__id=client_id)
        client = Client.objects.get(id=client_id)
        if not scorm_assignments:
            messages.warning(request, "No SCORM packages assigned to this client")
    except ScormAssignment.DoesNotExist:
        messages.error(request, "Error fetching SCORM assignments")
        scorm_assignments = None
    return render(request, 'coreadmin/client_manage_scorm.html',
                  {'scorm_assignments': scorm_assignments, 'client': client})


def scorm_iframe(request, scorm_id):
    scorm = get_object_or_404(ScormAsset, id=scorm_id)
    Activity.objects.create(
        user=request.user,
        activity_type=f'previewed SCORM: {scorm.title}',
        timestamp=datetime.now()
    )
    return render(request, 'coreadmin/scorm_iframe.html', {'scorm': scorm})


def assign_scorm(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    form = None
    try:
        if request.method == "POST":
            form = AssignSCORMForm(request.POST)
            if form.is_valid():
                logger.info("Form is valid. Saving...")
                form.save(client)
                logger.info(f"Successfully saved ScormAssignment for client_id={client_id}")

                Activity.objects.create(
                    user=request.user,
                    activity_type=f'assigned SCORM to Client: {client.first_name} {client.last_name}',
                    timestamp=datetime.now()
                )

                return redirect("manage_scorm", client_id=client_id)
            else:
                logger.error(f"Form validation failed with errors: {form.errors}")
        else:
            form = AssignSCORMForm(initial={'client': client})
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        messages.error(request, f"An error occurred: {str(e)}")
    return render(request, "coreadmin/client_assign_scorm.html", {"form": form, "client": client})


def create_client(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            try:
                client = form.save(commit=False)
                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password1'],
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data.get('last_name', "")
                )
                client.user = user
                client.save()

                Activity.objects.create(
                    user=request.user,
                    activity_type=f'created new Client: {client.first_name} {client.last_name}',
                    timestamp=datetime.now()
                )

                messages.success(request, 'Client created successfully!')
                logger.info(f"Client {client.id} created successfully.")
                return JsonResponse({'success': True})
            except IntegrityError as e:
                if 'unique constraint' in str(e):
                    logger.error(f"Error creating client: Username already exists.")
                    return JsonResponse({'success': False, 'error': 'Username already exists.'})
                else:
                    logger.error(f"Error creating client: {str(e)}")
                    logger.error(traceback.format_exc())  # Print the traceback
                    return JsonResponse({'success': False, 'error': str(e)})
            except Exception as e:
                logger.error(f"Error creating client: {e}")
                logger.error(traceback.format_exc())  # Print the traceback
                return JsonResponse({'success': False, 'error': 'An unexpected error occurred.'})
        else:
            logger.error(f"Form validation failed with errors: {form.errors}")
            return JsonResponse({'success': False, 'errors': form.errors.as_json()})
    else:
        form = ClientForm()
    return render(request, 'coreadmin/create_client.html', {'form': form})


def get_client_details(request, client_id):
    client = Client.objects.get(pk=client_id)
    data = {
        "first_name": client.first_name,
        "last_name": client.last_name,
        "company": client.company,
        "email": client.email,
        "contact_phone": client.contact_phone,
        "domains": client.domains,
        "lms_url": client.lms_url,
        "lms_api_key": client.lms_api_key,
        "lms_api_secret": client.lms_api_secret,
    }
    return JsonResponse(data)


def client_update_view(request, client_id):
    client = get_object_or_404(Client, id=client_id)

    if request.method == "POST":
        if (
                "HTTP_X_REQUESTED_WITH" in request.META
                and request.META["HTTP_X_REQUESTED_WITH"] == "XMLHttpRequest"
        ):
            form = ClientUpdateForm(request.POST, instance=client)
            if form.is_valid():
                form.save()

                Activity.objects.create(
                    user=request.user,
                    activity_type=f'updated Client: {client.first_name} {client.last_name} details',
                    timestamp=datetime.now()
                )
                return JsonResponse({"success": True})
            else:
                return JsonResponse({"success": False, "errors": form.errors})
        else:
            form = ClientUpdateForm(request.POST, instance=client)
            if form.is_valid():
                form.save()
                messages.success(request, "Client updated successfully")

                Activity.objects.create(
                    user=request.user,
                    activity_type=f'updated Client: {client.first_name} {client.last_name} details',
                    timestamp=datetime.now()
                )

                return redirect("client_list")
    else:
        form = ClientUpdateForm(instance=client)

    return render(request, "coreadmin/client_list.html", {"form": form})


def get_user_details(request, client_id, user_id):
    client = get_object_or_404(Client, id=client_id)
    user = get_object_or_404(ClientUser, id=user_id)
    data = {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "scorm_consumed": user.scorm_consumed,
        "learner_id": user.learner_id,
        "cloudscorm_user_id": user.cloudscorm_user_id,
    }
    return JsonResponse(data)


def user_update_view(request, client_id, user_id):
    client = get_object_or_404(Client, id=client_id)
    user = get_object_or_404(ClientUser, id=user_id)

    if request.method == "POST":
        if (
                "HTTP_X_REQUESTED_WITH" in request.META
                and request.META["HTTP_X_REQUESTED_WITH"] == "XMLHttpRequest"
        ):
            form = UserUpdateForm(request.POST, instance=user)
            if form.is_valid():
                form.save()

                Activity.objects.create(
                    user=request.user,
                    activity_type=f'updated ClientUser: {user.first_name} {user.last_name} details',
                    timestamp=datetime.now()
                )
                return JsonResponse({"success": True})
            else:
                logger.error(f"Form errors: {form.errors}")
                return JsonResponse({"success": False, "errors": form.errors})
        else:
            form = UserUpdateForm(request.POST, instance=user)
            if form.is_valid():
                form.save()
                messages.success(request, "User updated successfully")

                Activity.objects.create(
                    user=request.user,
                    activity_type=f'updated ClientUser: {user.first_name} {user.last_name} details',
                    timestamp=datetime.now()
                )

                return redirect("client_user_list", client_id=client_id)
            else:
                logger.error(f"Form errors: {form.errors}")
    else:
        form = UserUpdateForm(instance=user)

    return render(request, "coreadmin/client_user_list.html", {"form": form, "client": client, "user": user})


def get_scorm_details(request, scorm_id):
    scorm = ScormAsset.objects.get(pk=scorm_id)
    data = {
        "title": scorm.title,
        "course_code": scorm.course_code,
        "category": scorm.category,
        "duration": scorm.duration,
        "scorm_id": scorm.scorm_id,
        "launch_url": scorm.launch_url,
        "short_description": scorm.short_description,
        "long_description": scorm.long_description,
        "cover_photo": request.build_absolute_uri(scorm.cover_photo.url) if scorm.cover_photo else None,
    }
    return JsonResponse(data)


def scorm_update_view(request, scorm_id):
    scorm = get_object_or_404(ScormAsset, id=scorm_id)

    if request.method == "POST":
        if (
                "HTTP_X_REQUESTED_WITH" in request.META
                and request.META["HTTP_X_REQUESTED_WITH"] == "XMLHttpRequest"
        ):
            form = ScormUpdateForm(request.POST, instance=scorm)
            if form.is_valid():
                form.save()
                activity = Activity.objects.create(
                    user=request.user,
                    activity_type=f'updated Scorm: {scorm.title} details',
                    timestamp=datetime.now()
                )
                activity.save()
                return JsonResponse({"success": True})
            else:
                return JsonResponse({"success": False, "errors": form.errors})
        else:
            form = ScormUpdateForm(request.POST, instance=scorm)
            if form.is_valid():
                form.save()
                messages.success(request, "Client updated successfully")

                activity = Activity.objects.create(
                    user=request.user,
                    activity_type=f'updated Scorm: {scorm.title} details',
                    timestamp=datetime.now()
                )
                activity.save()

                return redirect("scorm_list")
    else:
        form = ScormUpdateForm(instance=scorm)

    return render(request, "coreadmin/scorm_list.html", {"form": form})


def client_user_profile(request, client_id, user_id):
    client = get_object_or_404(Client, id=client_id)
    user = get_object_or_404(ClientUser, id=user_id)
    return render(request, 'coreadmin/client_user_profile.html', {'client': client, 'user': user})


def client_user_mapped_scorm(request, client_id, user_id):
    client = get_object_or_404(Client, id=client_id)
    user = get_object_or_404(ClientUser, id=user_id)
    scorms = UserScormMapping.objects.filter(user=user)
    return render(request, 'coreadmin/client_user_mapped_scorm.html',
                  {'client': client, 'user': user, 'scorms': scorms})


def client_user_mapped_scorm_progress(request, client_id, user_id, scorm_id):
    client = get_object_or_404(Client, id=client_id)
    user = get_object_or_404(ClientUser, id=user_id)
    scorm = get_object_or_404(ScormAsset, id=scorm_id)
    scorm_status = UserScormStatus.objects.filter(client_user=user, _scorm_id=scorm.scorm_id).first()

    return render(request, 'coreadmin/client_user_mapped_scorm_progress.html',
                  {'client': client, 'user': user, 'scorm': scorm, 'scorm_status': scorm_status})
