from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.http import JsonResponse

@api_view(['GET'])
def health_check(request):
    return JsonResponse({"status": "ok"}, status=status.HTTP_200_OK)


@api_view(['POST'])
def Generate_questions(request):
    topic = request.data.get('topic')
    
    if not topic:
        return JsonResponse({"error": "Topic is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Simulate question generation
    questions = [
        {"question": f"What is {topic}?", "answer": f"{topic} is a concept."},
        {"question": f"Explain {topic}.", "answer": f"{topic} is explained here."}
    ]

    return JsonResponse({"questions": questions}, status=status.HTTP_200_OK)

# @api_view(['POST'])
