from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import ResumeUploadSerializer  # Ensure this exists
import bcrypt
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from backend.settings import db 

# ----------------------------- SIGN UP API -----------------------------

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])  # Added this to fix 401 error
def signup(request):
    try:
        data = json.loads(request.body)
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        confirm_password = data.get("confirm_password")

        if not name or not email or not password or not confirm_password:
            return Response({"error": "All fields are required"}, status=400)
            
        # Basic email validation
        if '@' not in email or '.' not in email:
            return Response({"error": "Invalid email format"}, status=400)

        if password != confirm_password:
            return Response({"error": "Passwords do not match"}, status=400)
            
        # Basic password strength check
        if len(password) < 8:
            return Response({"error": "Password must be at least 8 characters long"}, status=400)

        user_collection = db["users"]

        if user_collection.find_one({"email": email}):
            return Response({"error": "User already exists"}, status=400)

        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        user_collection.insert_one({"name": name, "email": email, "password": hashed_password.decode()})

        return Response({"message": "User registered successfully"}, status=201)

    except Exception as e:
        print("Signup Error:", str(e))
        # Don't expose actual error details to client
        return Response({"error": "Registration failed. Please try again."}, status=500)
    
# ------------------------------------------- LOGIN API ------------------------------------------------------------
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    try:
        data = json.loads(request.body)
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return Response({"error": "All fields are required"}, status=400)
            
        # Basic email validation
        if '@' not in email or '.' not in email:
            return Response({"error": "Invalid email format"}, status=400)
        
        user_collection = db['users']
        user = user_collection.find_one({"email": email})

        if not user:
            return Response({"error": "No user exists-register first"}, status=404)
        
        if not bcrypt.checkpw(password.encode(), user["password"].encode()):
            return Response({"error": "Incorrect email or password"}, status=401)
        
        # FIX: Create RefreshToken directly instead of using for_user
        refresh = RefreshToken()
        
        # Add custom claims to identify the user
        refresh['user_id'] = str(user.get('_id'))
        refresh['email'] = user.get('email')
        refresh['name'] = user.get('name')
        
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "name": user.get('name'),
                "email": user.get('email')
            }
        }, status=200)
    except Exception as e:
        print("Login Error:", str(e))
        return Response({"error": "Internal Server Error"}, status=500)   

# ---------------------------------------------------------

@api_view(['POST'])
@permission_classes([AllowAny])  # Also adding this here to be consistent
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