from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from .serializers import ResumeUploadSerializer  # Ensure this exists
import bcrypt
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from backend.settings import db 

# ----------------------------- SIGN UP API -----------------------------

@csrf_exempt
@api_view(['POST'])
def signup(request):
    try:
        data = json.loads(request.body)
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        confirm_password = data.get("confirm_password")

        if not name or not email or not password or not confirm_password:
            return Response({"error": "All fields are required"}, status=400)

        if password != confirm_password:
            return Response({"error": "Passwords do not match"}, status=400)

        user_collection = db["users"]

        if user_collection.find_one({"email": email}):
            return Response({"error": "User already exists"}, status=400)

        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        user_collection.insert_one({"name": name, "email": email, "password": hashed_password.decode()})

        return Response({"message": "User registered successfully"}, status=201)

    except Exception as e:
        print("Signup Error:", str(e))  
        return Response({"error": str(e)}, status=500)

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])  # Required for file uploads
def upload_resume(request):
    print("Received Data:", request.data)  # Debugging: Print received data
    
    serializer = ResumeUploadSerializer(data=request.data)
    
    if serializer.is_valid():
        file = serializer.validated_data['file']
        job_description = serializer.validated_data['job_description']
        
        print("Uploaded File:", file.name)  # Print file name
        print("Job Description:", job_description)  # Print job description
        
        return Response({"message": "File received successfully!"}, status=200)

    return Response(serializer.errors, status=400)
