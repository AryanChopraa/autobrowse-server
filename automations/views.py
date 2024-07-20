# backend/views.py
from django.http import JsonResponse
from .models import Automation
import json
import uuid
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_task(request):
    if request.method == 'POST':
        user = request.user
        data = json.loads(request.body)
        task_description = data.get('objective')

        if not task_description:
            return JsonResponse({'error': 'Invalid task description'}, status=400)

        session_id = str(uuid.uuid4())

        automation = Automation.objects.create(
            user=user,
            objective=task_description,
            session_id=session_id,
        )

        return JsonResponse({
            'sessionId': session_id,
        }, status=201)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fetch_tasks(request):
    user = request.user
    automations = Automation.objects.filter(user=user).values('id', 'objective', 'session_id', 'created_on')
    return JsonResponse(list(automations), safe=False)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fetch_task(request, session_id):
    user = request.user

    automation = get_object_or_404(Automation, session_id=session_id, user=user)

    task_data = {
        'id': automation.id,
        'objective': automation.objective,
        'session_id': str(automation.session_id),
        'created_on': automation.created_on,
    }
    
    return JsonResponse(task_data)

