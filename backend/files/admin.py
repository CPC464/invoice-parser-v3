from django.contrib import admin
from .models import File


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    """
    Admin configuration for the File model
    """

    list_display = ("id", "filename", "original_file_name", "uploaded_at", "updated_at")
    list_filter = ("uploaded_at", "updated_at")
    search_fields = ("original_file_name", "user_defined_file_name")
    readonly_fields = ("id", "original_file_name", "uploaded_at", "updated_at")
    fieldsets = (
        (
            None,
            {"fields": ("id", "file", "original_file_name", "user_defined_file_name")},
        ),
        (
            "Timestamps",
            {"fields": ("uploaded_at", "updated_at"), "classes": ("collapse",)},
        ),
    )
