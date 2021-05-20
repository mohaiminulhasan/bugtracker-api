import json
from itertools import chain
from operator import attrgetter

from datetime import datetime
from django.shortcuts import render
import rest_framework
from rest_framework.response import Response
from rest_framework import generics, permissions
from rest_framework.decorators import api_view

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

from .models import Project, TicketOrder, Ticket, TicketHistory, TicketComment
from .serializers import (
    ProjectSerializer,
    TicketSerializer, 
    UserSerializer, 
    TicketHistorySerializer,
    TicketCommentSerializer
)

# Create your views here.
class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        now = datetime.now()
        then = datetime(1970, 1, 1)
        auth_validity_time = 60 * 60 # in seconds
        time_in_seconds = round((now-then).total_seconds() + auth_validity_time)

        return Response({
            'message': 'Login success!',
            'token': token.key,
            'expiresAt': time_in_seconds,
            'userInfo': {
                'id': user.pk,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            },
        })

class ProjectsListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        owned_projects = Project.objects.filter(owner=self.request.user)
        assigned_projects = self.request.user.project_set.all()
        return sorted(
            chain(owned_projects, assigned_projects),
            key=attrgetter('created')
            )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class OwnedProjectListAPIView(generics.ListAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)

# use permission
# @api_view(http_method_names=['GET'])
# def ticket_list_by_status(request, projectslug):
#     project = Project.objects.get(slug=projectslug)
#     output = {}
#     statuses = ['IB', 'EM', 'IP', 'TS', 'CO']
#     for status in statuses:
#         output[status] = TicketSerializer(Ticket.objects.filter(project=project, status=status), many=True).data
    
#     return Response(output)

@api_view(http_method_names=['GET'])
def ticket_list(request, projectslug):
    statuses = {
        'IB': 'Ice Box',
        'EM': 'Emergency',
        'IP': 'In Progress',
        'TS': 'Testing',
        'CO': 'Complete'
    }

    output = {
        'tickets': {},
        'columns': {}
    }

    project = Project.objects.get(slug=projectslug)
    tickets = Ticket.objects.filter(project=project)
    for ticket in tickets:
        output['tickets'][ticket.id] = TicketSerializer(ticket).data

    for key in statuses:
        status_obj, created = TicketOrder.objects.get_or_create(project=project, status=key)
        # ticket_ids = Ticket.objects.filter(project=project, status=key).values_list('id', flat=True)
        output['columns'][key] = {
            'id': key,
            'title': statuses[key],
            'ticketIds': status_obj.get_tickets()
        }

    return Response(output)

class SingleUserListAPIView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        project = Project.objects.get(slug=self.kwargs['projectslug'])

        owner = User.objects.filter(id=project.owner.id)
        team_users = project.users.all()
        single_users = User.objects.all().difference(team_users, owner)
        
        return single_users

# use permission
@api_view(http_method_names=['GET'])
def team_user_list(request, projectslug):
    project = Project.objects.get(slug=projectslug)
    output = []
    for user in project.users.all():
        obj = { 'id': user.id, 'username': user.username, 'isAdmin': False }
        if (user in project.admins.all()):
            obj['isAdmin'] = True
        output.append(obj.copy())
    return Response(output) 

# use permission
@api_view(http_method_names=['PUT'])
def add_to_team(request, username, projectslug):
    user = User.objects.get(username=username)
    project = Project.objects.get(slug=projectslug)
    if (user not in project.users.all()):
        project.users.add(user)
        return Response({ 'response': 'OK', 'id': user.id })
    return Response({ 'response': 'Invalid' })

# use permission
@api_view(http_method_names=['PUT'])
def remove_from_team(request, username, projectslug):
    user = User.objects.get(username=username)
    project = Project.objects.get(slug=projectslug)
    if (user in project.users.all()):
        project.users.remove(user)
        if (user in project.admins.all()):
            project.admins.remove(user)
        return Response({ 'response': 'OK', 'id': user.id })
    return Response({ 'response': 'Invalid' })

# user permission
@api_view(http_method_names=['POST'])
def toggle_as_admin(request, username, projectslug):
    user = User.objects.get(username=username)
    project = Project.objects.get(slug=projectslug)
    if (user in project.users.all()):
        if (user in project.admins.all()):
            project.admins.remove(user)
            return Response({ 'response': 'OK', 'isAdmin': False })
        else:
            project.admins.add(user)
            return Response({ 'response': 'OK', 'isAdmin': True })
    return Response({ 'response': 'Invalid' })

# class TicketUpdateAPIView(generics.UpdateAPIView):
#     queryset = Ticket.objects.all()
#     serializer_class = TicketSerializer
#     permission_classes = [permissions.IsAuthenticated]

@api_view(http_method_names=['PATCH'])
def move_ticket(request, source, sourceindex, destination, destinationindex):
    project = Project.objects.get(slug=request.data['project'])
    sourceObj = TicketOrder.objects.get(project=project, status=source)
    sourceOrder = sourceObj.get_tickets()
    if (source == destination):
        try:
            item = sourceOrder.pop(sourceindex)
            sourceOrder.insert(destinationindex, item)
            sourceObj.set_tickets(sourceOrder)
            return (Response({ 'response': 'OK' }))
        except:
            return (Response({ 'response': 'Invalid' }))
    else:
        destinationObj = TicketOrder.objects.get(project=project, status=destination)
        destinationOrder = destinationObj.get_tickets()
        try:
            item = sourceOrder.pop(sourceindex)
            destinationOrder.insert(destinationindex, item)
            sourceObj.set_tickets(sourceOrder)
            destinationObj.set_tickets(destinationOrder)
            return Response({ 'response': 'OK' })
        except:
            return Response({ 'response': 'Invalid' }, status=404)

class TicketRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

# user permission
@api_view(http_method_names=['POST'])
def create_ticket(request):
    username, project, status, title = [request.data[i] for i in ('username', 'project', 'status', 'title')]
    user = User.objects.get(username=username)
    project = Project.objects.get(slug=project)
    ticket = Ticket.objects.create(title=title, submitter=user, project=project, status=status)

    ticketorder = TicketOrder.objects.get(project=project, status=status)
    data = ticketorder.get_tickets()
    data.insert(0, ticket.id)
    ticketorder.set_tickets(data)
    return Response({
        'ticket': TicketSerializer(ticket).data,
        'order': data
    })

class TicketHistoryListAPIView(generics.ListAPIView):
    serializer_class = TicketHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TicketHistory.objects.filter(ticket_id=self.kwargs['pk'])

class TicketCommentListAPIView(generics.ListAPIView):
    serializer_class = TicketCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TicketComment.objects.filter(ticket_id=self.kwargs['pk'])

class TicketDeleteAPIView(generics.DestroyAPIView):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

class TicketUpdateAPIView(generics.UpdateAPIView):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]