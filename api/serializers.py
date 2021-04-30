from rest_framework import serializers

from .models import Project, Ticket
from django.contrib.auth.models import User


class ProjectSerializer(serializers.ModelSerializer):
  class Meta:
    model = Project
    fields = ['id', 'created', 'owner', 'title', 'slug']

class TicketSerializer(serializers.ModelSerializer):
  class Meta:
    model = Ticket
    fields = ['id', 'title', 'description', 'developer', 'submitter', 'priority', 'status']

class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ['id', 'username']