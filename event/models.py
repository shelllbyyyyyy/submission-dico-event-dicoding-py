from django.db import models
import uuid

from auth.models import User

class Event(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    name = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField()
    location = models.CharField(max_length=100, null=False, blank=False)
    status = models.CharField(max_length=100, null=False, blank=False)
    quota = models.IntegerField(null=False, blank=False)
    category = models.CharField(max_length=100, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'events'

class EventOrganizer(models.Model):
    event_organizer_id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'event_organizers'
        constraints = [
            models.UniqueConstraint(
                fields=["user", "event"],
                name="uq_event_organizers"
            )
        ]
        indexes = [
            models.Index(fields=['event'], name='idx_event_organizers_event_id'),
        ]

class EventSession(models.Model):
    event_session_id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    event = models.ForeignKey(Event, related_name='sessions', on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'event_sessions'
        constraints = [
            models.CheckConstraint(
                check=models.Q(
                    end_time__date=models.F('start_time__date')
                ),
                name='chk_event_session_time'
            )
        ]
        indexes = [
            models.Index(fields=['event'], name='idx_event_sessions_event_id'),
        ]

