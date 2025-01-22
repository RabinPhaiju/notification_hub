from .models import Notification
from .serializers import NotificationSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import viewsets,status
from rest_framework.response import Response

class NotificationViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    def list(self, request, *args, **kwargs):
        # Get the default response from the parent class
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        
        # Wrap the response in {'result': []}
        custom_response = {'result': serializer.data}
        
        return Response(custom_response)

    def create(self, request, *args, **kwargs):
        return Response({"detail": "Method not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        return Response({"detail": "Method not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        return Response({"detail": "Method not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)