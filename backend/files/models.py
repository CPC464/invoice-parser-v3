import os
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


def file_upload_path(instance, filename):
    """
    Generate a unique path for uploaded files
    Files are stored in MEDIA_ROOT/uploads/uuid-originalfilename
    """
    ext = filename.split(".")[-1]
    filename = f"{instance.id}.{ext}"
    return os.path.join("uploads", filename)


class File(models.Model):
    """
    Model for storing uploaded files with original and optional user-defined names
    """

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_("File ID")
    )
    original_file_name = models.CharField(
        max_length=255, verbose_name=_("Original File Name")
    )
    user_defined_file_name = models.CharField(
        max_length=255, blank=True, null=True, verbose_name=_("User Defined File Name")
    )
    file = models.FileField(upload_to=file_upload_path, verbose_name=_("File"))
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Uploaded At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("File")
        verbose_name_plural = _("Files")
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.user_defined_file_name or self.original_file_name

    def filename(self):
        """
        Return the user-defined name if available, otherwise the original name
        """
        return self.user_defined_file_name or self.original_file_name
