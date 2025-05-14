from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.http import JsonResponse

@api_view(['GET'])
def health_check(request):
    return JsonResponse({"status": "ok"}, status=status.HTTP_200_OK)