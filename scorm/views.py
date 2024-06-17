from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse, FileResponse, Http404, HttpResponseBadRequest
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
import requests
import json
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

from clients.models import Client
from .models import ScormAsset, ScormAssignment, ScormResponse, UserScormMapping, UserScormStatus
from .forms import AssignSCORMForm, ScormAssetForm
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

class ScormUploadView(CreateView):
    model = ScormAsset
    form_class = ScormAssetForm
    template_name = 'coreadmin/upload_scorm.html'
    success_url = reverse_lazy('scorm_list')

    def form_valid(self, form):
        try:
            self.object = form.save(commit=False)  # Don't save to the database yet
        except Exception as e:
            logger.error(f"Error saving form: {str(e)}")
            return super().form_invalid(form)

        try:
            # Get the Bearer token from settings
            bearer_token = "c1ff48c3e772fdc4363b283728fa37f992fea64fc8518cbd502812427d0a9186"
            headers = {'Authorization': f'Bearer {bearer_token}'}

            # Upload SCORM file to the API with Bearer token
            scorm_file = self.request.FILES['scorm_file']
            api_response = requests.post(
                'https://cloudscorm.cloudnuv.com/api/v1/scorm',
                files={'file': scorm_file},
                headers=headers,
                verify=True,
                timeout=600,
            )
        except Exception as e:
            logger.error(f"Error making API request: {str(e)}")
            form.add_error(None, 'Failed to upload SCORM to the API.')
            return super().form_invalid(form)

        if api_response.status_code == 200:
            try:
                response_data = api_response.content.decode("utf-8")
                response_data = json.loads(response_data)
                logger.debug(f"Response: {response_data}")

                if response_data.get("status") is True:
                    self.object.scorm_id = response_data.get("scorm")
                    self.object.save()
                    logger.info(f"SCORM uploaded successfully: {response_data.get('message')}")
                else:
                    logger.error(f"API request failed: {response_data.get('message')}")
                    form.add_error(None, response_data.get('message', 'Failed to upload SCORM to the API.'))
                    return super().form_invalid(form)
            except json.JSONDecodeError:
                logger.error(f"Error decoding JSON from response: {api_response.content}")
                form.add_error(None, 'Failed to process API response.')
                return super().form_invalid(form)
            except Exception as e:
                logger.error(f"Error processing API response: {str(e)}")
                form.add_error(None, 'Failed to process API response.')
                return super().form_invalid(form)
        else:
            logger.error(f"Failed to upload file. Status code: {api_response.status_code}")
            logger.error(f"Response content: {api_response.content}")
            form.add_error(None, 'Failed to upload SCORM to the API.')
            return super().form_invalid(form)

        return super().form_valid(form)