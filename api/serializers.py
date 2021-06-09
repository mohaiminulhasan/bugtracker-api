from django.db.models.fields import CharField
from rest_framework import serializers

from .models import Project, Ticket, TicketHistory, TicketComment
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ['id', 'username']

class ProjectSerializer(serializers.ModelSerializer):
  class Meta:
    model = Project
    fields = ['id', 'created', 'owner', 'title', 'slug']

class TicketSerializer(serializers.ModelSerializer):
  assignee = serializers.CharField(source='get_assignee')

  class Meta:
    model = Ticket
    fields = ['id', 'title', 'description', 'developer', 'assignee', 'submitter', 'priority', 'status']

class TicketHistorySerializer(serializers.ModelSerializer):
  class Meta:
    model = TicketHistory
    fields = ['field', 'old_value', 'new_value', 'created']

class TicketCommentSerializer(serializers.ModelSerializer):
  author = serializers.SlugRelatedField(
    read_only=True,
    slug_field='username'
  )

  class Meta:
    model = TicketComment
    fields = ['author', 'body', 'ticket', 'created']
