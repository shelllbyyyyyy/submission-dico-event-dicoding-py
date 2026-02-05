from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import  IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from auth.permissions import IsAdminOrSuperUser
from .models import Event
from .serializers import EventWriteSerializer, EventReadSerializer


class EventListCreateView(APIView):
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminOrSuperUser(), IsAuthenticated()]

        return [IsAuthenticated()]

    def get(self, request):
        events = Event.objects.all().order_by('-created_at')[:10].prefetch_related('sessions')
        serializer = EventReadSerializer(events, many=True, context={'request': request})
        return Response({ 'events': serializer.data }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = EventWriteSerializer(data=request.data)
        if serializer.is_valid():
            event = serializer.save()

            read_serializer = EventReadSerializer(
                event,
                context={'request': request}
            )
            return Response(read_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EventDetailView(APIView):
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.request.method != 'GET':
            return [IsAdminOrSuperUser(), IsAuthenticated()]
        return [IsAuthenticated()]

    def get_object(self, pk):
        try:
            event = Event.objects.prefetch_related('sessions').get(pk=pk)
            self.check_object_permissions(self.request, event)
            return event
        except Event.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        event = self.get_object(pk)
        serializer = EventReadSerializer(event)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        event = self.get_object(pk=pk)

        serializer = EventWriteSerializer(
            event,
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        event = serializer.save()

        return Response(
            EventReadSerializer(event, context={'request': request}).data, status=status.HTTP_200_OK
        )

    def delete(self, request, pk):
        event = self.get_object(pk=pk)
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
