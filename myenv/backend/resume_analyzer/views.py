from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import ResumeUploadSerializer

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])

def upload_resume(request):
    serializer = ResumeUploadSerializer(data=request.data)

    if serializer.is_valid():
        file = serializer.validated_data['file']
        job_description = serializer.validated_data['job_description']

        # TODO: Process file using AI later

        return Response({"message": "File received successfully!"}, status=200)
    
    return Response(serializer.errors, status=400)
