# coding=utf-8
""""
    API REST views
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2024-07-24'
__copyright__ = 'Copyright 2015 - 2024, Gis3w'
__license__ = 'MPL 2.0'

from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from huey.contrib.djhuey import HUEY
from huey import signals
from huey.exceptions import TaskException
from huey_monitor.models import TaskModel
from rest_framework.response import Response
from OWS.views import OWSView
from core.api.authentication import CsrfExemptSessionAuthentication
from qdjango.ows import OWSRequestHandler
from qdjango.models import Project
from core.api.base.views import G3WAPIView
from qpdnd.models import (
    QPDNDProject, 
    ANNCSUProject
)
from qpdnd.utils.pdnd import QPDNDAdapter
from qpdnd.tasks import (
    send_anncsu_pdnd_task, 
    send_anncsu_pdnd_ceery_task
)
from .permissions import ProjectEditPermission
from .decorators.voucher_checker import pdnd_voucher_required
from qgis.server import QgsServerProjectUtils

from django.test import Client
import json
from django.http import HttpResponse

from requests.exceptions import HTTPError
from requests.auth import HTTPBasicAuth
import requests

import logging

logger = logging.getLogger('qpdnd.anncsu')

class QDPNDOWSRequestHandler(OWSRequestHandler):

    def doRequest(self):
        """ Main proxy method entry """
        q = self.request.GET.copy()
        return self.baseDoRequest(q)


class QPDNDAPIOgcView(OWSView):
    """
    A wrapper view for QGIS server OCG WFS3 endpoint.
    """


    @method_decorator(csrf_exempt)
    @method_decorator(pdnd_voucher_required)
    def dispatch(self, request, *args, **kwargs):

        # Get parameters for OWS:ows-wfs3 url by endpoint url parameter
        self.qpdndp = QPDNDProject.objects.get(endpoint=kwargs['endpoint'])

        kwargs.update({
            'group_slug': self.qpdndp.project.group.slug,
            'project_id': self.qpdndp.project.pk,

        })

        # get handler request by project type
        self.OWSRequestHandler = QDPNDOWSRequestHandler

        # Delete endpoint parameter for
        del kwargs['endpoint']

        return super(OWSView, self).dispatch(request, *args, **kwargs)

    def _make_problem_json_response(self, msg:str, status_code:int=500) -> JsonResponse:
        """
        Return a JsonResponse with a content-type header set to application/problem+json
        """

        return JsonResponse({
            'status': status_code,
            'title': msg
        },
            status=status_code,
            **{'content_type': 'application/problem+json'})

    def get(self, request, *args, **kwargs):

        try:

            # Management fo `/status` response
            # https://italia.github.io/api-oas-checker/rulesets/spectral-modi.html
            # 'paths-status'
            # You must define a /status path that can be used to health-check the API. Using this path avoids the
            # arbitrary usage of a server URL for health-check scope.
            # The /status endpoint should return a application/problem+json response containing a successful status code
            # if the service is working correctly.
            # The service provider is free to define the implementation logic for this path.
            if '/wfs3/status' in request.path:
                return self._make_problem_json_response('OK', status_code=200)


            response = self.OWSRequestHandler(request, **kwargs).doRequest()

            # Check for possible problem
            if 400 <= response.status_code <= 499 or 500 <= response.status_code <= 599:
                return self._make_problem_json_response(response.content, response.status_code)

            # Check for api.openapi3 in request.path
            if '/wfs3/api.openapi3' in request.path:
                adapter = QPDNDAdapter(response, self.qpdndp)

                adapter.fix_italian_guidelines_extended()

                adapter.update_response()

                if 'download' in request.GET and request.GET['download'] == '1':
                    adapter.download()

                response = adapter.response

            return response

        except Exception as e:

            return self._make_problem_json_response(str(e), 500)


class QPDNDInfoProjectAPIView(G3WAPIView):

    permission_classes = [
        ProjectEditPermission
    ]

    def get(self, request, *args, **kwargs):

        prj = Project.objects.get(pk=kwargs['project_id'])
        qprj = prj.qgis_project

        toret = {}
        # Get OCG Server capabilitites properties:
        for service_property in [
            'Title',
            'Abstract',
            'OnlineResource',
            'ContactMail',
            'ContactPerson',

        ]:
            toret.update({
              service_property: getattr(
                QgsServerProjectUtils, f'owsService{service_property}')(qprj)
            })

        self.results.results.update(toret)
        return Response(self.results.results)

class ANNCSURunAPIView(G3WAPIView):
    """
    ANNCSU gestione coordinate API view
    """

    # permission_classes = [
    #     ProjectEditPermission
    # ]

    def get(self, request, *args, **kwargs):

        toret= {}

        anncsu_project = ANNCSUProject.objects.get(pk=kwargs['anncsu_project_id'])

        # Check for additional GET parameters if needed
        send_type = request.GET.get('send_type', None)

        # Send on Huey
        task = send_anncsu_pdnd_task(anncsu_project, send_type)

        logger.debug(f"Started task {task.id} for ANNCSU project {anncsu_project.pk} with send_type {send_type}")

        # Send on Celery
        # task = object()
        # task.id = send_anncsu_pdnd_ceery_task.delay(kwargs['anncsu_project_id'])

        anncsu_project.task_id = task.id
        anncsu_project.save()

        toret.update({
            'task_id': task.id,
        })

        self.results.results.update(toret)
        return Response(self.results.results)
    
class ANNCSURunInfoTaskView(G3WAPIView):
    """
    ANNCSU view to get progess state ok a huey/celery task.
    """

    def get(self, request, task_id):

        #TODO: add code for celery tasks.

        try:

            # Try to retrieve the task result, may throw an exception
            try:
                result = HUEY.result(task_id)
                
                # Retry 3 times if result is None
                retry_count = 0
                while result is None and retry_count < 3:
                    result = HUEY.result(task_id)
                    retry_count += 1
                ret_status = 200
            except TaskException:
                result = None
                ret_status = 500

            task_model = TaskModel.objects.get(task_id=task_id)
            progress_info = task_model.progress_info

            try:
                progress_percentage = int(
                    100 * progress_info[0] / task_model.total)
            except:
                progress_percentage = 0

            try:

                # Add current feature being processed

                try:
                    ap = ANNCSUProject.objects.get(task_id=task_id)
                    if not result:
                        result = {}
                    result.update({
                        'current_sent': len([f for f in ap.get_features(send_type='sent')]),
                        'current_error': len([f for f in ap.get_features(send_type='error')])
                    })
                except:
                    pass


                return JsonResponse({
                    'status': task_model.state.signal_name,
                    'exception': task_model.state.exception_line,
                    'progress': progress_percentage,
                    'task_result': result
                }, status=ret_status)
            except:
                return JsonResponse({
                    'status': 'error',
                    'exception': 'Error retrieving task informations',
                    'progress': 0,
                    'task_result': result,
                }, status=500)

        except TaskModel.DoesNotExist:

            # Handle pending
            pending_task_ids = [task.id for task in HUEY.pending()]

            if task_id in pending_task_ids:
                return JsonResponse({'result': True, 'status': 'pending'})

            return JsonResponse({'result': False, 'error': _('Task not found!')}, status=404)
        

class ANNCSURunKillTaskView(G3WAPIView):
    """
    ANNCSU view to kill a huey/celery task.
    """

    def get(self, request, task_id):
        """
        Stops a Huey task given the task_id
        """
        try:
            # Check if the task exists in the database
            task_model = TaskModel.objects.get(task_id=task_id)
            
            # Check if the task is still running
            if task_model.state.signal_name in [
                signals.SIGNAL_EXECUTING, 
                #signals.SIGNAL_ENQUEUED, 
                signals.SIGNAL_SCHEDULED
                ]:
                
                try:
                    
                    # For running tasks, Huey does not support direct interruption
                    # You can only mark the task as revoked
                    HUEY.revoke_by_id(task_id)
                    
                    # Update the state in the database
                    task_model.state.signal_name = signals.SIGNAL_REVOKED
                    task_model.state.save()
                    
                    return JsonResponse({
                        'status': signals.SIGNAL_REVOKED,
                        'message': 'Task revoked (may continue if already executing)',
                        'warning': 'Huey does not support forced interruption of running tasks'
                    }, status=200)
                    
                except Exception as e:
                    return JsonResponse({
                        'status': signals.SIGNAL_ERROR,
                        'error': f'Error revoking task: {str(e)}'
                    }, status=500)
            
            else:
                return JsonResponse({
                    'status': signals.SIGNAL_COMPLETE,
                    'message': f'Task already completed with state: {task_model.state.signal_name}'
                }, status=400)
                
        except TaskModel.DoesNotExist:

            # Handle pending
            pending_task_ids = [task.id for task in HUEY.pending()]

            if task_id in pending_task_ids:
                return JsonResponse({'result': True, 'status': 'pending'})

            return JsonResponse({'result': False, 'error': _('Task not found!')}, status=404)
        
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'error': str(e)
            }, status=500)


class ANNCSUDownTaskResultsView(G3WAPIView):
    """
    Donwload ANNCSU task results view
    """

    def get(self, request, task_id):
        """
        Download the results of a Huey task given the task_id
        """
        try:
            # Try to retrieve the task result, may throw an exception
            try:
                result = HUEY.result(task_id)

                # If result is None, try to get from ANNCSUPProject model
                if result is None:
                    raise TaskException("No result available for this task")
            except TaskException:
                # Try to get from ANNCSUPProject model
                try:
                    ap = ANNCSUProject.objects.get(task_id=task_id)
                    if ap.results:
                        result = ap.results
                    else:
                       return JsonResponse({
                        'status': 'error',
                        'error': 'No results available for this task'
                    }, status=404)
                
                except ANNCSUProject.DoesNotExist:
                    return JsonResponse({
                    'status': 'error',
                    'error': 'Error retrieving task results'
                }, status=500)

            # Return the results as a JSON response
            response = HttpResponse(
                json.dumps({'status': 'success', 'task_result': result}, indent=2),
                content_type='application/json'
            )
            response['Content-Disposition'] = f'attachment; filename="task_{task_id}_results.json"'
            return response

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'error': str(e)
            }, status=500)  
        

class ANNCSURunCONSCOMAPIView(G3WAPIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication,
    )

    def post(self, request, *args, **kwargs):

        try:
            anncsu_project = ANNCSUProject.objects.get(pk=kwargs['anncsu_project_id'])
            payload = request.data['payload']

            try:
                service = kwargs['service']
            except:

                # Try to get from payload
                try:
                    service = json.loads(payload)['req']
                except:
                    return JsonResponse({
                        'status': 'error', 
                        'error': 'Missing `req` in payload or service as parameter'
                    },status=400)
            
            # Make apiurl by service    
            api_url = f"{anncsu_project.govway_api_endpoint}/{service}"


            if not service or not payload:
                return JsonResponse({
                    'status': 'error', 
                    'error': 'Missing service or payload in request body'
                },status=400)

            if anncsu_project.govway_username and anncsu_project.govway_password:
                auth = HTTPBasicAuth(anncsu_project.govway_username, anncsu_project.govway_password)
            else:       
                auth = HTTPBasicAuth(settings.ANNCSU_GOVWAY_API_USER, settings.ANNCSU_GOVWAY_API_PASSWORD)


            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }

            
            response = requests.post(
                api_url,
                headers=headers,
                json=json.loads(payload),
                auth=auth
            )
            
            #logger.debug(f"[ANNCSU] - {response.json()}")
            response.raise_for_status()
            
            



            # For demonstration, we'll just return the received data
            return JsonResponse({
                'status': 'success', 
                'service': service, 
                'payload': response.json()
            }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error', 
                'error': 'Invalid JSON in request body'
            }, status=400)
        
        except HTTPError as http_err:
            return JsonResponse({
                'status': 'error', 
                'error': f'HTTP error occurred: {str(http_err)}: {http_err.response.text if http_err.response.text else "No response content"}'
            }, status=response.status_code if response else 500)

        except Exception as e:
            return JsonResponse({
                'status': 'error', 
                'error': str(e)
            }, status=500)
        