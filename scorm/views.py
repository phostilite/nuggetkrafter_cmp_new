from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse, FileResponse, Http404
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

from clients.models import Client
from .models import ScormAsset, ScormAssignment, ScormResponse, UserScormMapping, UserScormStatus
from .forms import AssignSCORMForm
from api.models import Activity, Notification

def get_all_scorms(request):
    try:
        scorms = ScormAsset.objects.all()
        form = AssignSCORMForm()
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        scorms = []
        form = None
    return render(request, "scorm/get_all_scorms.html", {"scorms": scorms, "form": form})


def download_scorm(request, client_id, scorm_id):
    try:
        client = get_object_or_404(Client, pk=client_id)
        scorm = get_object_or_404(ScormAsset, pk=scorm_id)

        assignment = ScormAssignment.objects.filter(
            client=client, scorm_asset=scorm
        ).first()

        if not assignment:
            raise PermissionDenied("You do not have access to this SCORM")

        if not os.path.exists(assignment.client_scorm_file.path):
            raise Http404("File not found")

        file = open(assignment.client_scorm_file.path, "rb")
    except (Http404, PermissionDenied):
        raise
    except Exception as e:
        return HttpResponse(f"An error occurred: {str(e)}", status=500)

    response = FileResponse(file, content_type="application/zip")
    filename = f"{client.first_name}_{client_id}_{scorm.title}_wrapper.zip"  
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    Activity.objects.create(
        user=request.user,
        activity_type=f'downloaded SCORM wrapper {filename}',
        timestamp=datetime.now()
    )
    return response
