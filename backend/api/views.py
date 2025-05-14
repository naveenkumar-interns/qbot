from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.http import JsonResponse

import os
import json
import ast
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
    

# @api_view(['GET'])
# def evaluate_answers(request):
#     user = request.GET.get('user')
#     if not user:
#         return JsonResponse({"error": "User is required"}, status=status.HTTP_400_BAD_REQUEST)
#     try:
#         # Fetch the test data
#         user_data = questions_collection.find_one({"user": user})
#         if not user_data or "test" not in user_data:
#             return JsonResponse({"error": "No test data found for this user"}, status=status.HTTP_400_BAD_REQUEST)
#         test = user_data["test"]

#         # Use AI to evaluate each answer
#         results = []
#         for q in test:
#             prompt = f"""
# You are an examiner. Compare the following correct answer and user answer for the question below. 
# Give a score of 1 if the user's answer is correct or mostly correct, otherwise 0. 
# Return only the score (0 or 1) avoid preamble and do not include any other text.

# Question: {q['question']}
# Correct Answer: {q['answer']}
# User Answer: {q['user_answer']}
# """
#             ai_score = llm.invoke(prompt).content.strip()
#             try:
#                 ai_score = int(ai_score)
#             except Exception:
#                 ai_score = 0
#             results.append(ai_score)

#         total_count = len(test)
#         correct_count = sum(results)
#         score = (correct_count / total_count) * 100 if total_count > 0 else 0

#         print(f"Score: {score}, Correct Count: {correct_count}, Total Count: {total_count}")

#         return JsonResponse({"score": score, "details": results}, status=status.HTTP_200_OK)
#     except Exception as e:
#         return JsonResponse({"error": "Failed to evaluate answers"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
import re
import json

def extract_json(text):
    try:
        # Remove ```json and ``` markers if present
        text = text.strip()
        text = re.sub(r'^```json\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'\s*```$', '', text, flags=re.MULTILINE)        
        # Try to parse the cleaned text as JSON
        print(f"Extracting JSON from text: {json.loads(text)}")
        return json.loads(text)
    except json.JSONDecodeError as e:
        # Log the problematic text for debugging
        print(f"JSON parsing error: {str(e)}")
        print(f"Raw text: {text}")
        raise ValueError(f"Failed to parse JSON: {str(e)}")
    except Exception as e:
        print(f"Unexpected error in extract_json: {str(e)}")
        print(f"Raw text: {text}")
        raise ValueError(f"Unexpected error: {str(e)}")

@api_view(['GET'])
def evaluate_answers(request):
    user = request.GET.get('user')
    if not user:
        return JsonResponse({"error": "User is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Fetch the test data
        user_data = questions_collection.find_one({"user": user})
        if not user_data or "test" not in user_data:
            return JsonResponse({"error": "No test data found for this user"}, status=status.HTTP_400_BAD_REQUEST)
        test = user_data["test"]

        # Use AI to evaluate each answer and provide feedback
        results = []
        updated_test = []
        for q in test:
            prompt = f"""
            You are an examiner. Compare the following correct answer and user answer for the question below.
            - Give a score of 1 if the user's answer is correct or mostly correct, otherwise 0.
            - Briefly explain why you gave this score.
            - Suggest how the user could improve their answer if it was not perfect.

            Return your response as a JSON object with keys: score, reason, suggestion.
            Example:
            {{"score": 1, "reason": "The answer is correct.", "suggestion": ""}}
            or
            {{"score": 0, "reason": "The answer misses key points.", "suggestion": "Include more details about ..."}}

            Question: {q['question']}
            Correct Answer: {q['answer']}
            User Answer: {q['user_answer']}
            """
            try:
                ai_response = llm.invoke(prompt).content.strip()
                print(f"AI Response for question : {ai_response}")
                feedback = extract_json(ai_response)
                
                # Validate feedback structure
                if not isinstance(feedback, dict) or "score" not in feedback or "reason" not in feedback or "suggestion" not in feedback:
                    raise ValueError("AI response JSON missing required keys: score, reason, suggestion")
                
                score = int(feedback.get("score", 0))
                reason = feedback.get("reason", "No reason provided.")
                suggestion = feedback.get("suggestion", "No suggestion provided.")

            except Exception as e:
                print(f"Error processing AI response: {str(e)}")
                score = 0
                reason = f"Failed to process AI response: {str(e)}"
                suggestion = "Please try again or contact support."
                feedback = {"score": score, "reason": reason, "suggestion": suggestion}

            results.append(score)
            # Update each test item with feedback
            updated_q = dict(q)
            updated_q.update({
                "score": score,
                "reason": reason,
                "suggestion": suggestion
            })
            updated_test.append(updated_q)

        total_count = len(test)
        correct_count = sum(results)
        overall_score = (correct_count / total_count) * 100 if total_count > 0 else 0

        # Store the updated test with feedback in the DB
        questions_collection.update_one(
            {"user": user},
            {"$set": {"test": updated_test}},
            upsert=True
        )

        return JsonResponse({
            "score": overall_score,
            "details": updated_test
        }, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"Unexpected error in evaluate_answers: {str(e)}")
        return JsonResponse({"error": f"Failed to evaluate answers: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
def get_evaluations(request):
    user = request.data.get('user')
    if not user:
        return JsonResponse({"error": "User is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Fetch the test data
        user_data = questions_collection.find_one({"user": user})
        if not user_data or "test" not in user_data:
            return JsonResponse({"error": "No test data found for this user"}, status=status.HTTP_400_BAD_REQUEST)
        test = user_data["test"]

        return JsonResponse({"test": test}, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"Unexpected error in get_evaluations: {str(e)}")
        return JsonResponse({"error": f"Failed to get evaluations: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)