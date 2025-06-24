from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from .models import Resume, ResumeVersion
from .serializers import ResumeSerializer, ResumeVersionSerializer
from .services.s3_service import S3Service
import uuid

class ResumeUploadView(APIView):
    """
    API endpoint for uploading a new resume.
    """
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get("file")
        resume_name = request.data.get("name", file_obj.name if file_obj else "Untitled Resume")
        user_id = request.user.id
        if not file_obj:
            return Response({"error": "File not provided"}, status=status.HTTP_400_BAD_REQUEST)
        resume = Resume.objects.create(name=resume_name, user_id=user_id)
        s3_service = S3Service()
        s3_key = f"resumes/{user_id}/{resume.id}/initial/{file_obj.name}"
        if not s3_service.upload_file(file_obj, s3_key):
            resume.delete()
            return Response({"error": "Failed to upload file to S3"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        resume_version = ResumeVersion.objects.create(
            resume=resume,
            file_path=s3_key,
            file_name=file_obj.name,
            file_size=file_obj.size,
            file_type=file_obj.content_type,
            comment="Initial version"
        )
        serializer = ResumeSerializer(resume)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ResumeListView(APIView):
    """
    API endpoint for listing all resumes of the current user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        resumes = Resume.objects.filter(user_id=request.user.id)
        serializer = ResumeSerializer(resumes, many=True)
        return Response(serializer.data)

class ResumeDetailView(APIView):
    """
    API endpoint for retrieving or deleting a specific resume.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, resume_id, *args, **kwargs):
        try:
            resume = Resume.objects.get(id=resume_id, user_id=request.user.id)
        except Resume.DoesNotExist:
            return Response({"error": "Resume not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ResumeSerializer(resume)
        return Response(serializer.data)

    def delete(self, request, resume_id, *args, **kwargs):
        try:
            resume = Resume.objects.get(id=resume_id, user_id=request.user.id)
        except Resume.DoesNotExist:
            return Response({"error": "Resume not found"}, status=status.HTTP_404_NOT_FOUND)
        resume.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ResumeVersionListView(APIView):
    """
    API endpoint for listing all versions of a resume or uploading a new version.
    """
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def get(self, request, resume_id, *args, **kwargs):
        versions = ResumeVersion.objects.filter(resume__id=resume_id, resume__user_id=request.user.id)
        serializer = ResumeVersionSerializer(versions, many=True)
        return Response(serializer.data)

    def post(self, request, resume_id, *args, **kwargs):
        try:
            resume = Resume.objects.get(id=resume_id, user_id=request.user.id)
        except Resume.DoesNotExist:
            return Response({"error": "Resume not found"}, status=status.HTTP_404_NOT_FOUND)
        file_obj = request.FILES.get("file")
        comment = request.data.get("comment", "New version")
        if not file_obj:
            return Response({"error": "File not provided"}, status=status.HTTP_400_BAD_REQUEST)
        s3_service = S3Service()
        new_version_id = uuid.uuid4()
        s3_key = f"resumes/{request.user.id}/{resume.id}/{new_version_id}/{file_obj.name}"
        if not s3_service.upload_file(file_obj, s3_key):
            return Response({"error": "Failed to upload file to S3"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        resume_version = ResumeVersion.objects.create(
            id=new_version_id,
            resume=resume,
            file_path=s3_key,
            file_name=file_obj.name,
            file_size=file_obj.size,
            file_type=file_obj.content_type,
            comment=comment
        )
        serializer = ResumeVersionSerializer(resume_version)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class FileDownloadView(APIView):
    """
    API endpoint for downloading a resume file.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, file_id, *args, **kwargs):
        try:
            resume_version = ResumeVersion.objects.get(id=file_id, resume__user_id=request.user.id)
        except ResumeVersion.DoesNotExist:
            return Response({"error": "File not found or access denied"}, status=status.HTTP_404_NOT_FOUND)
        s3_service = S3Service()
        file_content = s3_service.download_file(resume_version.s3_key)
        if file_content is None:
            return Response({"error": "Failed to download file from S3"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        response = HttpResponse(file_content, content_type=resume_version.file_type)
        response["Content-Disposition"] = f"attachment; filename={resume_version.file_name}"
        return response

class FileDeleteView(APIView):
    """
    API endpoint for deleting a resume file.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, file_id, *args, **kwargs):
        try:
            resume_version = ResumeVersion.objects.get(id=file_id, resume__user_id=request.user.id)
        except ResumeVersion.DoesNotExist:
            return Response({"error": "File not found or access denied"}, status=status.HTTP_404_NOT_FOUND)
        s3_service = S3Service()
        if not s3_service.delete_file(resume_version.s3_key):
            return Response({"error": "Failed to delete file from S3"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        resume_version.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
