from rest_framework import serializers
from rest_framework.reverse import reverse
from django.db import transaction

from .models import Event, EventSession, EventOrganizer
from auth.models import User

class EventWriteSerializer(serializers.ModelSerializer):
    start_time = serializers.DateTimeField(write_only=True)
    end_time = serializers.DateTimeField(write_only=True)
    organizer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True
    )

    class Meta:
        model = Event
        fields = [
            'id',
            'name',
            'status',
            'category',
            'description',
            'location',
            'start_time',
            'end_time',
            'quota',
            'organizer_id',
        ]

    def validate(self, data):
        if data['end_time'] <= data['start_time']:
            raise serializers.ValidationError(
                "end_time must be greater than start_time"
            )
        return data

    def create(self, validated_data):
        start_time = validated_data.pop('start_time')
        end_time = validated_data.pop('end_time')
        organizer = validated_data.pop('organizer_id')

        with transaction.atomic():
            event = Event.objects.create(**validated_data)

            EventSession.objects.create(
                event=event,
                start_time=start_time,
                end_time=end_time
            )

            EventOrganizer.objects.create(
                event=event,
                user=organizer
            )

        return event

    def update(self, instance, validated_data):
        start_time = validated_data.pop('start_time', None)
        end_time = validated_data.pop('end_time', None)
        organizer = validated_data.pop('organizer_id', None)

        with transaction.atomic():
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            if start_time or end_time:
                session, _ = EventSession.objects.get_or_create(
                    event=instance
                )

                if start_time:
                    session.start_time = start_time
                if end_time:
                    session.end_time = end_time

                if session.end_time <= session.start_time:
                    raise serializers.ValidationError(
                        "end_time must be greater than start_time"
                    )

                session.save()

            if organizer:
                EventOrganizer.objects.update_or_create(
                    event=instance,
                    defaults={'user': organizer}
                )

        return instance

class EventReadSerializer(serializers.HyperlinkedModelSerializer):
    _links = serializers.SerializerMethodField()
    start_time = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()
    organizer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        source='event_organizers'
    )

    class Meta:
        model = Event
        fields = [
            'id',
            'name',
            'status',
            'category',
            'description',
            'location',
            'start_time',
            'end_time',
            'quota',
            'organizer_id',
            '_links'
        ]

    def get_start_time(self, obj):
        session = obj.sessions.first()
        return session.start_time if session else None

    def get_end_time(self, obj):
        session = obj.sessions.first()
        return session.end_time if session else None

    def get__links(self, obj):
        request = self.context.get('request')
        return [
            {
                "rel": "self",
                "href": reverse('event-list', request=request),
                "action": "POST",
                "types": ["application/json"]
            },
            {
                "rel": "self",
                "href": reverse('event-detail', kwargs={'pk': obj.pk}, request=request),
                "action": "GET",
                "types": ["application/json"]
            },
            {
                "rel": "self",
                "href": reverse('event-detail', kwargs={'pk': obj.pk}, request=request),
                "action": "PUT",
                "types": ["application/json"]
            },
            {
                "rel": "self",
                "href": reverse('event-detail', kwargs={'pk': obj.pk}, request=request),
                "action": "DELETE",
                "types": ["application/json"]
            }
        ]