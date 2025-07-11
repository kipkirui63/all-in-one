
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def api_status(request):
    return Response({
        'status': 'ok',
        'message': 'API is running'
    })
