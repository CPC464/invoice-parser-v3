from rest_framework import serializers
from .models import File


class FileSerializer(serializers.ModelSerializer):
    """
    Serializer for the File model
    """

    file_url = serializers.SerializerMethodField()

    class Meta:
        model = File
        fields = [
            "id",
            "original_file_name",
            "user_defined_file_name",
            "file",
            "file_url",
            "uploaded_at",
            "updated_at",
        ]
        read_only_fields = ["id", "original_file_name", "uploaded_at", "updated_at"]

    def get_file_url(self, obj):
        """
        Get the full URL for the file
        """
        request = self.context.get("request")
        if request and obj.file:
            return request.build_absolute_uri(obj.file.url)
        return None
