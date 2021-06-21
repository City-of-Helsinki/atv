from rest_framework import status, viewsets
from rest_framework.response import Response


class DocumentsViewSet(viewsets.ViewSet):
    def create(self, request):
        return Response({"status": "CREATED"}, status=status.HTTP_201_CREATED)
