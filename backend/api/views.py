from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.http import JsonResponse

import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from pymongo import MongoClient

# MongoDB connection
client = MongoClient("mongodb+srv://rohit:Rohit2004@cluster45.61avwkq.mongodb.net/")
db = client["test_agent"]
questions_collection = db["questions"]



# Set Google API Key for Gemini
if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = "AIzaSyDNM_3iF_QCRm0y4QNBiPfRdM5u4YRoHCU"

# Initialize the Gemini model
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    temperature=0.7,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)



@api_view(['GET'])
def health_check(request):
    return JsonResponse({"status": "ok"}, status=status.HTTP_200_OK)



def store_questions(questions,user):
    """
    Store the generated questions in the MongoDB collection.
    """
    try:
        # Insert the questions into the MongoDB collection
        data = {
            "user": user,
            "questions": questions
        }
        # Check if the user already exists
        existing_user = questions_collection.find_one({"user": user})
        if existing_user:
            # Update the existing user's questions
            questions_collection.update_one({"user": user}, {"$set": {"questions": questions}})
        else:
            # Insert a new user with the questions
            questions_collection.insert_one(data)
        return True
    except Exception as e:
        print(f"Error storing questions: {e}")
        return False







@api_view(['POST'])
def Generate_questions(request):
    topic = request.data.get('topic')
    user = request.data.get('user')
    if not user:
        return JsonResponse({"error": "User is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    if not topic:
        return JsonResponse({"error": "Topic is required"}, status=status.HTTP_400_BAD_REQUEST)

    prompt_template = ChatPromptTemplate([
    ("system", """You are a helpful assistant that generates questions based on a given topic. 
                 The format of the output should be a list of 5 questions in the following format:
                [
                {{"question": "Question 1", "answer": "Answer 1"}},
                {{"question": "Question 2", "answer": "Answer 2"}}
                ]
        avoid preamble and do not include any other text.
        """
     ),
    ("user", "{topic}")
])
    chain = prompt_template | llm
    result = chain.invoke({"topic": topic}).content
    
    # Convert the result to a list of dictionaries
    try:
        result = eval(result)
    except Exception as e:
        return JsonResponse({"error": "Failed to parse the response from the model"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    if not isinstance(result, list):
        return JsonResponse({"error": "Invalid response format, try again"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    if not store_questions(result, user) :
        return JsonResponse({"error": "Failed to store questions"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return JsonResponse({"questions": result}, status=status.HTTP_200_OK)






@api_view(['GET'])
def get_questions(request):
    user = request.GET.get('user')
    if not user:
        return JsonResponse({"error": "User is required"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        user_data = questions_collection.find_one({"user": user})
        if not user_data or "questions" not in user_data:
            return JsonResponse({"questions": []}, status=status.HTTP_200_OK)
        return JsonResponse({"questions": user_data["questions"]}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({"error": "Failed to fetch questions"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    



@api_view(['POST'])
def submit_answers(request):
    user = request.data.get('user')
    user_answers = request.data.get('answers')
    if not user or not user_answers:
        return JsonResponse({"error": "User and answers are required"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        # Fetch the original questions and answers
        user_data = questions_collection.find_one({"user": user})
        if not user_data or "questions" not in user_data:
            return JsonResponse({"error": "No questions found for this user"}, status=status.HTTP_400_BAD_REQUEST)
        questions = user_data["questions"]

        # Merge questions, correct answers, and user answers
        test = []
        for idx, q in enumerate(questions):
            test.append({
                "question": q.get("question"),
                "answer": q.get("answer"),
                "user_answer": user_answers[idx]["answer"] if idx < len(user_answers) else ""
            })

        # Store in the new format
        questions_collection.update_one(
            {"user": user},
            {"$set": {"test": test}},
            upsert=True
        )
        return JsonResponse({"message": "Answers submitted successfully"}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({"error": "Failed to submit answers"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)