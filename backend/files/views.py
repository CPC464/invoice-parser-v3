from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import File
from .serializers import FileSerializer

# Create your views here.


@extend_schema_view(
    list=extend_schema(description="List all files"),
    retrieve=extend_schema(description="Retrieve a specific file"),
    create=extend_schema(description="Upload a new file"),
    update=extend_schema(description="Update file metadata (not the file itself)"),
    partial_update=extend_schema(description="Partially update file metadata"),
    destroy=extend_schema(description="Delete a file"),
)
class FileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows files to be viewed, uploaded, edited, and deleted.
    """

    queryset = File.objects.all()
    serializer_class = FileSerializer

    def perform_create(self, serializer):
        """
        Save the original filename when creating a new file
        """
        file_obj = self.request.FILES.get("file")
        if file_obj:
            serializer.save(original_file_name=file_obj.name)
