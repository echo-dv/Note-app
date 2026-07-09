from django.http import JsonResponse
from django.db import connections
from django.db.utils import OperationalError


def liveness(request):
    return JsonResponse({"status": "ok"}, status=200)


def readiness(request):
    db_conn = connections["default"]
    try:
        with db_conn.cursor() as cursor:
            cursor.execute("SELECT 1;")

        return JsonResponse({"status": "ok"}, status=200)

    except OperationalError:
        return JsonResponse({"status": "error"}, status=503)
