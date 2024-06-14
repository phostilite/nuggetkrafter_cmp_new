import logging
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from scorm.models import ScormAsset, ScormAssignment, ScormResponse, UserScormMapping, UserScormStatus
from clients.models import Client, ClientUser
from scorm.forms import AssignSCORMForm
from clients.forms import ClientUpdateForm, UserUpdateForm

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
    return render(request, 'coreadmin/client_manage_scorm.html', {'scorm_assignments': scorm_assignments, 'client': client})


def assign_scorm(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    return render(request, 'coreadmin/client_assign_scorm.html', {'client': client})

def scorm_iframe(request, scorm_id):
    scorm = get_object_or_404(ScormAsset, id=scorm_id)
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
                return redirect("manage_scorm", client_id=client_id)
            else:
                logger.error(f"Form validation failed with errors: {form.errors}")
        else:
            form = AssignSCORMForm(initial={'client': client})
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        messages.error(request, f"An error occurred: {str(e)}")
    return render(request, "coreadmin/client_assign_scorm.html", {"form": form, "client": client})


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
                return JsonResponse({"success": True})
            else:
                return JsonResponse({"success": False, "errors": form.errors})
        else:
            form = ClientUpdateForm(request.POST, instance=client)
            if form.is_valid():
                form.save()
                messages.success(request, "Client updated successfully")
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
                return JsonResponse({"success": True})
            else:
                logger.error(f"Form errors: {form.errors}")
                return JsonResponse({"success": False, "errors": form.errors})
        else:
            form = UserUpdateForm(request.POST, instance=user)
            if form.is_valid():
                form.save()
                messages.success(request, "User updated successfully")
                return redirect("client_user_list", client_id=client_id)
            else:
                logger.error(f"Form errors: {form.errors}")
    else:
        form = UserUpdateForm(instance=user)

    return render(request, "coreadmin/client_user_list.html", {"form": form, "client": client, "user": user})