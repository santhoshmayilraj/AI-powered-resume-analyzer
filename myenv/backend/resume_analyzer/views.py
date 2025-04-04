from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import ResumeUploadSerializer
import bcrypt
import json
import datetime
from django.views.decorators.csrf import csrf_exempt
from backend.settings import db
from .authentication import MongoJWTAuthentication

# ----------------------------- SIGN UP API -----------------------------

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
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
        
        # Create RefreshToken directly instead of using for_user
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

# ------------------------------------------- UPLOAD RESUME API ------------------------------------------------------------

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser]) 
def upload_resume(request):
    try:
        # Extract user_id from the MongoDBUser instance
        user_id = None
        
        # Now that we're using MongoDBUser, we can access id directly
        if hasattr(request.user, 'id'):
            user_id = request.user.id
        
        if not user_id:
            return Response({"error": "User identification failed. Please login again."}, status=401)
        
        print(f"Received resume upload from user: {user_id}")
        
        serializer = ResumeUploadSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({"error": serializer.errors}, status=400)
            
        file = serializer.validated_data['file']
        job_description = serializer.validated_data['job_description']
        
        # Check file type
        allowed_extensions = ['.pdf', '.doc', '.docx']
        file_extension = '.' + file.name.split('.')[-1].lower()
        
        if file_extension not in allowed_extensions:
            return Response({
                "error": "Invalid file type. Only PDF, DOC, and DOCX files are supported."
            }, status=400)
            
        # Check file size (limit to 5MB)
        if file.size > 5 * 1024 * 1024:  # 5MB in bytes
            return Response({
                "error": "File too large. Maximum file size is 5MB."
            }, status=400)
        
        # Read file content
        file_content = file.read()
        
        # Create resume document
        resume_data = {
            'user_id': user_id,
            'filename': file.name,
            'content_type': file.content_type,
            'file_size': file.size,
            'file_data': file_content,
            'job_description': job_description,
            'upload_date': datetime.datetime.now(),
            'analysis_results': {
                'status': 'pending',
                'score': None,
                'keywords_matched': [],
                'missing_keywords': [],
                'recommendations': []
            }
        }
        
        # Insert into MongoDB
        resume_collection = db['resumes']
        result = resume_collection.insert_one(resume_data)
        
        # Return success response with the resume ID
        return Response({
            "message": "Resume uploaded successfully!",
            "resume_id": str(result.inserted_id)
        }, status=200)
        
    except Exception as e:
        print("Resume Upload Error:", str(e))
        return Response({"error": "Failed to upload resume. Please try again."}, status=500)

# ------------------------------------------- GET USER RESUMES API -------------------------------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_resumes(request):
    try:
        # Extract user_id from token payload
        user_id = None
        if hasattr(request, 'auth') and isinstance(request.auth, dict):
            user_id = request.auth.get('user_id')
        
        if not user_id:
            # Try getting it from the token payload directly
            if hasattr(request, 'user') and hasattr(request.user, 'user_id'):
                user_id = request.user.user_id
                
        if not user_id:
            return Response({"error": "User identification failed"}, status=401)
        
        # Get resumes for this user
        resume_collection = db['resumes']
        user_resumes = list(resume_collection.find(
            {"user_id": user_id},
            {"file_data": 0}  # Exclude file data to reduce response size
        ))
        
        # Format response data
        resumes_data = []
        for resume in user_resumes:
            resumes_data.append({
                "id": str(resume.get('_id')),
                "filename": resume.get('filename'),
                "upload_date": resume.get('upload_date').strftime("%Y-%m-%d %H:%M:%S"),
                "job_description": resume.get('job_description')[:100] + "..." if len(resume.get('job_description', "")) > 100 else resume.get('job_description', ""),
                "analysis_status": resume.get('analysis_results', {}).get('status', 'pending'),
                "score": resume.get('analysis_results', {}).get('score')
            })
        
        return Response({
            "resumes": resumes_data
        }, status=200)
        
    except Exception as e:
        print("Get Resumes Error:", str(e))
        return Response({"error": "Failed to retrieve resumes"}, status=500)