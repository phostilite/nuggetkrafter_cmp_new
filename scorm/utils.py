import bsdiff4
import base64
import json
import requests
import os
import tempfile
import shutil
import zipfile
import logging
from django.conf import settings
from django.core.files import File

logger = logging.getLogger(__name__)

def encrypt_data(client_id, scorm) -> str:
    data = (str(client_id) + "-" + str(scorm)).encode()
    base64_encoded_data = base64.b64encode(data)
    return base64_encoded_data.decode()


def decrypt_data(base64_encoded_data) -> str:
    base64_decoded_data = base64.b64decode(base64_encoded_data)
    return base64_decoded_data.decode()


def replace_placeholders(temp_wrapper_dir, client_specific_data):
    logger.info(f"Starting to replace placeholders in {temp_wrapper_dir}")
    logger.info(f"Client specific data: {client_specific_data}")

    def replace_placeholders_in_file(file_path, placeholders):
        logger.info(f"Starting to replace placeholders in {file_path}")
        if os.path.exists(file_path):
            logger.info(f"Path exists: {file_path}")
            with open(file_path, "r+") as file:
                contents = file.read()
                new_contents = contents
                for placeholder, value in placeholders.items():
                    if placeholder == "ID" and "configuration.js" in file_path:
                        parts = new_contents.split(placeholder)
                        if len(parts) >= 4:
                            parts[1] = value
                            parts[3] = value
                            new_contents = ''.join(parts)
                    else:
                        new_contents = new_contents.replace(placeholder, value)
                logger.info(f"New contents: {new_contents}")
                file.seek(0)
                file.write(new_contents)
                file.truncate()

    for root, dirs, files in os.walk(temp_wrapper_dir):
        for file in files:
            if file == "configuration.js":
                file_path = os.path.join(root, file)
                placeholders = {"ID": client_specific_data["id"]}
                replace_placeholders_in_file(file_path, placeholders)
            elif file == "imsmanifest.xml":
                file_path = os.path.join(root, file)
                placeholders = {"{{SCORM_TITLE}}": client_specific_data["scorm_title"]}
                replace_placeholders_in_file(file_path, placeholders)

def create_modified_scorm_wrapper(client_specific_data, assignment):
    scorm_wrapper_path = os.path.join(settings.MEDIA_ROOT, "scorm_wrapper", "scorm_wrapper_template.zip")
    temp_dir = tempfile.mkdtemp()
    temp_wrapper_dir = os.path.join(temp_dir, "scorm_wrapper")

    with zipfile.ZipFile(scorm_wrapper_path, "r") as zip_ref:
        zip_ref.extractall(temp_wrapper_dir)

    replace_placeholders(temp_wrapper_dir, client_specific_data)

    archive_path = os.path.join(temp_dir, "modified_wrapper.zip")
    with zipfile.ZipFile(archive_path, "w") as zip_ref:
        for root, dirs, files in os.walk(temp_wrapper_dir):
            for file in files:
                file_path = os.path.join(root, file)
                zip_ref.write(file_path, os.path.relpath(file_path, temp_wrapper_dir))  

    client_first_name = assignment.client.first_name.replace(" ", "_")
    client_id = assignment.client.id
    scorm_title = client_specific_data["scorm_title"].replace(" ", "_")  
    unique_filename = f"{client_first_name}_{client_id}_{scorm_title}_wrapper.zip"

    with open(archive_path, "rb") as file:
        assignment.client_scorm_file.save(unique_filename, File(file), save=True)

    shutil.rmtree(temp_dir)
    return assignment