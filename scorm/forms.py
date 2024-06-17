import os
from django.core.files import File
import logging
from django import forms
from django.conf import settings

from .models import ScormAsset, ScormAssignment, ScormResponse
from clients.models import Client
from .utils import encrypt_data, decrypt_data, create_modified_scorm_wrapper

logger = logging.getLogger(__name__)


class ScormAssetForm(forms.ModelForm):
    scorm_file = forms.FileField()

    class Meta:
        model = ScormAsset
        fields = ['title', 'short_description', 'long_description',
                  'course_code', 'category', 'duration', 'cover_photo', 'scorm_file']

class AssignSCORMForm(forms.ModelForm):
    scorms = forms.ModelMultipleChoiceField(
        queryset=ScormAsset.objects.all(), widget=forms.CheckboxSelectMultiple
    )
    client = forms.ModelChoiceField(
        queryset=Client.objects.all(), widget=forms.HiddenInput
    )
    validity_start_date = forms.DateTimeField(widget=forms.DateInput, required=False)
    validity_end_date = forms.DateTimeField(widget=forms.DateInput, required=False)

    class Meta:
        model = ScormAssignment
        fields = ["number_of_seats", "validity_start_date", "validity_end_date"]

    def save(self, client, commit=True):
        selected_scorms = self.cleaned_data["scorms"]
        number_of_seats = self.cleaned_data["number_of_seats"]
        validity_start_date = self.cleaned_data["validity_start_date"]
        validity_end_date = self.cleaned_data["validity_end_date"]
        assignments = []

        for scorm in selected_scorms:
            assignment = ScormAssignment(
                scorm_asset=scorm,
                client=client,
                number_of_seats=number_of_seats,
                validity_start_date=validity_start_date,
                validity_end_date=validity_end_date,
            )

            encrypted_id = encrypt_data(client.id, assignment.scorm_asset.id)
            logger.info(f"Encrypted ID: {encrypted_id}")
            client_specific_data = {"id": encrypted_id, "scorm_title": scorm.title, "referring_url": client.domains}

            assignment = create_modified_scorm_wrapper(
                client_specific_data,
                assignment,
            )

            if commit:
                assignment.save()
                scorm.save()  

            assignments.append(assignment)

        return assignments