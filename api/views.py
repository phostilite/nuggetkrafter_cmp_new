# Standard library imports
import os
import base64
import json
import logging
from datetime import datetime, timedelta
import random
import time

# Third party imports
from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import requests
import boto3
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie

# Local application imports
from clients.models import Client, ClientUser
from scorm.models import Course, Module, ScormAsset, ScormAssignment, ScormResponse, UserScormMapping, UserScormStatus
from scorm.utils import decrypt_data
from .utils import check_assigned_scorm_seats_limit, check_assigned_scorm_validity, construct_launch_url, \
    create_user_on_cloudscorm
from .models import Statistics, Activity, Notification
from django.utils.dateformat import format

logger = logging.getLogger(__name__)


@csrf_exempt
def validate_and_launch(request):
    # Get the encrypted ID, referring URL, and learner ID from the request data
    encrypted_id = request.GET.get("id")
    referring_url = request.GET.get("referringurl")
    learner_id = request.GET.get("learner_id")
    learner_name = request.GET.get("name")

    # Check if the required data is present
    if not all([encrypted_id, referring_url, learner_id, learner_name]):
        logger.error('Missing required data')
        return JsonResponse({"error": "Missing required data"}, status=400)

    # Decrypt the ID
    decrypted_id = decrypt_data(encrypted_id)

    # Split the decrypted ID to get the client ID and the SCORM ID
    client_id, scorm_id = decrypted_id.split("-")

    # Get the client
    try:
        client = Client.objects.get(id=client_id)
    except Client.DoesNotExist:
        logger.error('Invalid client identifier')
        return JsonResponse({"error": "Invalid client identifier"}, status=400)

    # Get the domain of the referring URL
    referring_domain = referring_url

    # Get the list of valid domains for the client
    valid_domains = client.domains.split(",")

    # Check if the referring domain is in the list of valid domains for the client
    if referring_domain not in valid_domains:
        logger.info("Invalid referring domain")
        return JsonResponse({"error": "Invalid referring domain"}, status=400)

    # Check if the SCORM assignment is valid
    if not check_assigned_scorm_validity(client_id, scorm_id):
        logger.info("License invalid")
        return JsonResponse({"error": "License invalid"}, status=400)

    # Check if the SCORM assignment seats limit is not exceeded
    if not check_assigned_scorm_seats_limit(client_id, scorm_id):
        logger.info("Seats limit exceeded")
        return JsonResponse({"error": "Seats limit exceeded"}, status=400)

    # Find or Create the ClientUser
    client_user, _ = ClientUser.objects.get_or_create(
        learner_id=learner_id, client=client, defaults={"first_name": learner_name}
    )

    # CloudScorm Sync
    bearer_token = settings.API_TOKEN1
    if not client_user.cloudscorm_user_id:
        cloudscorm_user_data = create_user_on_cloudscorm(learner_id, bearer_token)
        logger.info(f'CloudScorm User Data: {cloudscorm_user_data}')
        client_user.cloudscorm_user_id = cloudscorm_user_data["user_id"]
        client_user.save()

    scorm_asset = get_object_or_404(ScormAsset, id=scorm_id)
    assignment = get_object_or_404(ScormAssignment, scorm_asset=scorm_asset)

    # Create a UserScormMapping  
    UserScormMapping.objects.get_or_create(
        user=client_user,
        assignment=assignment
    )

    # Construct the launch URL
    launch_url = construct_launch_url(scorm_asset.scorm_id, client_user.cloudscorm_user_id)

    # Return the launch URL
    if launch_url:
        return JsonResponse({'launch_url': launch_url})
    else:
        logger.info("Failed to generate launch URL")
        return JsonResponse({"error": "Failed to generate launch URL"}, status=500)


def get_scorm_data(request, client_id, scorm_id):
    try:
        assignment = ScormAssignment.objects.get(client_id=client_id, scorm_asset_id=scorm_id)
        scorm = assignment.scorm_asset
        data = {
            "course_title": scorm.title,
            "course_code": str(int(time.time())) + str(random.randint(100, 999)),
            "cover_photo": request.build_absolute_uri(scorm.cover_photo.url),
            "short_description": scorm.description,
            "long_description": '',
            "modules": [{"type": 'scorm', "scorm_title": scorm.title,
                         "file": request.build_absolute_uri(assignment.client_scorm_file.url)}]
        }
        return JsonResponse(data, safe=False)
    except ScormAssignment.DoesNotExist:
        logger.exception("Scorm assignment not found")
        return JsonResponse({"error": "Scorm assignment not found"}, status=404)
    except Exception as e:
        logger.exception("An error occurred")
        return JsonResponse({"error": str(e)}, status=400)


def user_scorm_status(request):
    try:
        logger.info("Processing user_scorm_status request")

        id = request.GET.get('id')
        logger.info(f"ID: {id}")

        decoded_id = base64.b64decode(id).decode()
        client_id, scorm_id = decoded_id.split('-')
        logger.info(f"Client ID: {client_id}, SCORM ID: {scorm_id}")

        learner_id = request.GET.get('learner_id')
        logger.info(f"Learner ID: {learner_id}, Type: {type(learner_id)}")

        referringurl = request.GET.get('referringurl')
        logger.info(f"Referring URL: {referringurl}")

        # scorm
        scorm = ScormAsset.objects.get(id=scorm_id)
        logger.info(f"SCORM: {scorm}, Title: {scorm.title}")

        # learner
        client_user = ClientUser.objects.get(learner_id=learner_id)
        logger.info(f"Client User: {client_user}, Name: {client_user.first_name}")

        # client
        client = client_user.client
        logger.info(f"Client: {client}, Name: {client.first_name}")

        if client.domains != referringurl:
            logger.error("Invalid referring URL")
            return JsonResponse({"error": "Invalid referring URL"}, status=400)

        headers = {'Authorization': f'Bearer {settings.API_TOKEN1}'}
        url = f"https://cloudscorm.cloudnuv.com/user-status?user_id={client_user.cloudscorm_user_id}&scorm_id={scorm.scorm_id}"
        response = requests.post(url, headers=headers)

        if response.status_code in [200, 201]:
            stats = Statistics.objects.get(id=1)
            stats.status_checks += 1
            stats.save()

            data = response.json()
            reports = data.get('reports', [])
            logger.info(f"Reports: {reports}")

            if not reports:
                logger.error("Reports data is empty")
                return JsonResponse({"error": "Reports data is empty"}, status=400)

            user_scorm_status = None
            for report in reports:
                user_scorm_status, created = UserScormStatus.objects.update_or_create(
                    client_user=client_user,
                    _scorm_id=str(report['id']),
                    scorm_name=report['scormname'],
                    attempt=int(report['attempt']),
                    defaults={
                        'complete_status': report['complete_status'],
                        'satisfied_status': report['satisfied_status'],
                        'total_time': report['total_time'],
                        'score': report['score'],
                        'created_at': datetime.strptime(report['created_at'], '%Y-%m-%d %H:%M:%S'),
                        'updated_at': datetime.strptime(report['updated_at'], '%Y-%m-%d %H:%M:%S'),
                    }
                )
                break

            if user_scorm_status:
                logger.info("User SCORM status updated successfully")
                response_data = {
                    'learner_id': user_scorm_status.client_user.cloudscorm_user_id,
                    'learner_name': user_scorm_status.client_user.first_name,
                    'learner_email': user_scorm_status.client_user.email,
                    'scorm_id': user_scorm_status._scorm_id,
                    'scorm_name': user_scorm_status.scorm_name,
                    'complete_status': user_scorm_status.complete_status,
                    'satisfied_status': user_scorm_status.satisfied_status,
                    'total_time': user_scorm_status.total_time,
                    'score': user_scorm_status.score,
                    'attempt': user_scorm_status.attempt,
                    'created_at': user_scorm_status.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'updated_at': user_scorm_status.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                }
                return JsonResponse(response_data, status=200)
            else:
                logger.error("No UserScormStatus object found for the given SCORM ID")
                return JsonResponse({"error": "No UserScormStatus object found for the given SCORM ID"}, status=404)
        else:
            logger.error("Failed to get user SCORM status from API")
            return JsonResponse({"error": "Failed to get user SCORM status from API"}, status=400)
    except Exception as e:
        logger.exception("An error occurred in user_scorm_status")
        return JsonResponse({"error": str(e)}, status=400)


@require_POST
def sync_courses(request):
    try:
        # Validate and sanitize the request data
        data = json.loads(request.body)
        logger.info(f"Sync courses request data: {data}")
        client_id = data.get('clientId')
        scorm_id = data.get('scormId')

        if not client_id or not scorm_id:
            return JsonResponse({"error": "Missing required fields (clientId, scormId)"}, status=400)

        client = get_object_or_404(Client, id=client_id)
        scorm = get_object_or_404(ScormAsset, id=scorm_id)

        # Check if a Course object already exists for the given SCORM asset
        existing_course = Course.objects.filter(scorm_assets=scorm).first()

        if existing_course:
            course = existing_course
            course.title = data.get('course_title', course.title)
            course.code = data.get('course_code', course.code)  # Use course_code from data
            course.cover_photo = data.get('cover_photo', course.cover_photo)
            course.short_description = data.get('short_description', course.short_description)
            course.long_description = data.get('long_description', course.long_description)
        else:
            course = Course.objects.create(
                title=data.get('course_title', ''),
                code=data.get('course_code', ''),  # Use course_code from data
                cover_photo=data.get('cover_photo', ''),
                short_description=data.get('short_description', ''),
                long_description=data.get('long_description', ''),
            )
            course.scorm_assets.add(scorm)

        if not course.syncing_status:
            course.modules.all().delete()  # Delete existing modules

            for module_data in data.get('modules', []):
                try:
                    Module.objects.create(
                        course=course,
                        type=module_data.get('type', 'scorm'),
                        title=module_data.get('scorm_title', ''),
                        file=module_data.get('file', '')
                    )
                except ValidationError as e:
                    logger.error(f"Validation error while creating module: {e}")

            lms_url = f"{client.lms_url}/api/v1/course-create"
            LMS_API_KEY = client.lms_api_key
            LMS_API_SECRET = client.lms_api_secret

            credentials = base64.b64encode(f"{LMS_API_KEY}:{LMS_API_SECRET}".encode('utf-8')).decode('utf-8')
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Basic {credentials}',
            }
            logger.info(f"Sync courses request headers: {headers}")

            # Remove clientId and scormId from data
            data.pop('clientId', None)
            data.pop('scormId', None)

            logger.info(f"Sync courses request data: {data}")
            response = requests.post(lms_url, headers=headers, data=json.dumps(data))

            if response.status_code in [200, 201]:
                course.syncing_status = True
                course.save()
                return JsonResponse({"message": "Course created and synced successfully"}, status=201)
            else:
                logger.error(
                    f"Failed to sync course to client LMS. Status code: {response.status_code}, Response: {response.text}")
                return JsonResponse({
                    "error": f"Failed to sync course to client LMS. Status code: {response.status_code}, Response: {response.text}"},
                    status=400)

        else:
            return JsonResponse({"message": "Course already synced"}, status=200)

    except Exception as e:
        logger.exception("An error occurred in sync_courses")
        return JsonResponse({"error": str(e)}, status=400)


def get_scorm_data(request, client_id, scorm_id):
    try:
        assignment = ScormAssignment.objects.get(client_id=client_id, scorm_asset_id=scorm_id)
        scorm = assignment.scorm_asset
        data = {
            "course_title": scorm.title,
            "course_code": str(int(time.time())) + str(random.randint(100, 999)),
            "cover_photo": request.build_absolute_uri(scorm.cover_photo.url),
            "short_description": scorm.description,
            "long_description": '',
            "modules": [{"type": 'scorm', "scorm_title": scorm.title,
                         "file": request.build_absolute_uri(assignment.client_scorm_file.url)}]
        }
        return JsonResponse(data, safe=False)
    except ScormAssignment.DoesNotExist:
        logger.exception("Scorm assignment not found")
        return JsonResponse({"error": "Scorm assignment not found"}, status=404)
    except Exception as e:
        logger.exception("An error occurred")
        return JsonResponse({"error": str(e)}, status=400)


def reset_user_scorm_status(request):
    try:
        id = request.GET.get('id')
        decoded_id = base64.b64decode(id).decode()
        client_id, scorm_id = decoded_id.split('-')

        learner_id = request.GET.get('learner_id')
        referringurl = request.GET.get('referringurl')

        scorm = ScormAsset.objects.get(id=scorm_id)
        client_user = ClientUser.objects.get(learner_id=learner_id)
        client = client_user.client

        if client.domains != referringurl:
            return JsonResponse({"error": "Invalid referring URL"}, status=400)

        url = f"https://cloudscorm.cloudnuv.com/resetScormStatus?user_id={client_user.cloudscorm_user_id}&scorm_id={scorm.scorm_id}"
        headers = {"Authorization": f"Bearer {settings.API_TOKEN1}"}
        response = requests.post(url, headers=headers)

        if response.status_code in [200, 201]:
            stats = Statistics.objects.get(id=1)
            stats.resets += 1
            stats.save()
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"error": "Failed to reset SCORM status"}, status=400)

    except Exception as e:
        logger.exception("An error occurred")
        return JsonResponse({"error": str(e)}, status=400)


def server_status_api(request):
    logger.info("------ Starting server_status_api request ------")
    try:
        session = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name='ap-southeast-2'
        )
        logger.info("Boto3 session created with provided credentials")
        cloudwatch = session.client('cloudwatch')
        ec2 = session.resource('ec2')
        logger.info("CloudWatch and EC2 clients initialized")
        instance_id = settings.INSTANCE_ID
        logger.info(f"Target instance ID: {instance_id}")
        logger.info("Fetching CloudWatch StatusCheckFailed metric")
        status_check_failed = cloudwatch.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='StatusCheckFailed',
            Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
            StartTime=datetime.utcnow() - timedelta(minutes=5),
            EndTime=datetime.utcnow(),
            Period=60,
            Statistics=['Average']
        ).get('Datapoints', [])
        logger.info(f"StatusCheckFailed datapoints: {status_check_failed}")
        server_status = 'Not Operational' if any(dp['Average'] > 0 for dp in status_check_failed) else 'Operational'
        logger.info(f"Determined server status: {server_status}")
        try:
            logger.info("Fetching instance launch time")
            instance = ec2.Instance(instance_id)
            instance_launch_time = instance.launch_time
            logger.info(f"Retrieved launch time: {instance_launch_time}")
            uptime_seconds = (datetime.utcnow() - instance_launch_time.replace(tzinfo=None)).total_seconds()
            logger.info(f"Calculated uptime in seconds: {uptime_seconds}")
            uptime_str = str(timedelta(seconds=int(uptime_seconds)))
            logger.info(f"Uptime: {uptime_str}")
        except Exception as e:
            logger.error(f"Error fetching launch time: {e}")
            uptime_str = "N/A (Error fetching launch time)"
        instance_details = {
            'instance_id': instance.instance_id,
            'instance_type': instance.instance_type,
            'instance_state': instance.state['Name'],
            'launch_time': instance.launch_time.isoformat(),
            'private_ip': instance.private_ip_address,
            'public_ip': instance.public_ip_address,
            'public_ip': instance.public_ip_address,
            'availability_zone': instance.placement['AvailabilityZone'],
            'subnet_id': instance.subnet_id,
            'vpc_id': instance.vpc_id,
            'uptime': uptime_str,
        }
        data = {
            'server_status': server_status,
            'instance_details': instance_details,
        }
        logger.info("Preparing JSON response")
        logger.info("------ Completed server_status_api request ------")
        return JsonResponse(data)
    except Exception as e:
        logger.error(f"Error in server_status_api: {e}")
        return JsonResponse({'error': 'An error occurred while fetching server status'}, status=500)


@vary_on_cookie
@cache_page(60 * 15)
def stats_view(request):
    try:
        stats = cache.get('statistics')

        if not stats:
            stats = Statistics.objects.get(id=1)
            cache.set('statistics', stats, 60 * 15)

        statistics_data = {
            'clients': stats.clients,
            'users': stats.users,
            'scorm_packages': stats.scorm_packages,
            'assignments': stats.assignments,
            'resets': stats.resets,
            'status_checks': stats.status_checks,
        }

        return JsonResponse({'statistics_data': statistics_data})

    except Statistics.DoesNotExist:
        logger.error('Statistics object does not exist')
        return JsonResponse({'error': 'Statistics object does not exist'}, status=404)

    except Exception as e:
        logger.error(f'An error occurred: {str(e)}')
        return JsonResponse({'error': 'An error occurred'}, status=500)


def activities_view(request):
    try:
        limit = int(request.GET.get('limit', 5))
        activities = Activity.objects.order_by('-timestamp')[:limit]
        activities_data = [
            {
                'message': f'{activity.user.first_name} {activity.user.last_name} {activity.activity_type} at {format(activity.timestamp, "jS F Y H:i:s")}',
            }
            for activity in activities]
        return JsonResponse({'activities_data': activities_data})
    except Exception as e:
        logger.error(f'An error occurred while fetching activities: {str(e)}')
        return JsonResponse({'error': 'An error occurred while fetching activities'}, status=500)


def notifications_view(request):
    try:
        limit = int(request.GET.get('limit', 5))
        notifications = Notification.objects.order_by('-timestamp')[:limit]
        notifications_data = [{'message': notification.message, 'timestamp': notification.timestamp} for notification in
                              notifications]
        return JsonResponse({'notifications_data': notifications_data})
    except Exception as e:
        logger.error(f'An error occurred while fetching notifications: {str(e)}')
        return JsonResponse({'error': 'An error occurred while fetching notifications'}, status=500)


def fetch_client_users(request):
    try:
        limit = int(request.GET.get('limit', 5))
        client_users = ClientUser.objects.all()[:limit]
        client_users_data = [
            {
                'id': client_user.id,
                'first_name': client_user.first_name,
                'last_name': client_user.last_name,
                'email': client_user.email,
                'client': f'{client_user.client.first_name} {client_user.client.last_name}',
                'learner_id': client_user.learner_id,
                'cloudscorm_user_id': client_user.cloudscorm_user_id,
                'scorm_consumed': client_user.scorm_consumed,
            }
            for client_user in client_users
        ]
        return JsonResponse({'client_users_data': client_users_data})
    except Exception as e:
        logger.error(f'An error occurred while fetching client users: {str(e)}')
        return JsonResponse({'error': 'An error occurred while fetching client users'}, status=500)


def fetch_clients(request):
    try:
        limit = int(request.GET.get('limit', 5))
        clients = Client.objects.all()[:limit]
        clients_data = [
            {
                'id': client.id,
                'first_name': client.first_name,
                'last_name': client.last_name,
                'email': client.email,
                'contact_phone': client.contact_phone,
                'company': client.company,
            }
            for client in clients
        ]
        return JsonResponse({'clients_data': clients_data})
    except Exception as e:
        logger.error(f'An error occurred while fetching clients: {str(e)}')
        return JsonResponse({'error': 'An error occurred while fetching clients'}, status=500)
