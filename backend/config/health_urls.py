from django.http import JsonResponse
from django.urls import path


def health_check(request):
    """
    Simple health check endpoint that returns a 200 OK response
    """
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("", health_check, name="health_check"),
]
