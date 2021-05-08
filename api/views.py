from itertools import chain
from operator import attrgetter

from datetime import datetime
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import generics, permissions
from rest_framework.decorators import api_view

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

from .models import Project, Ticket, TicketHistory, TicketComment
from .serializers import (
    ProjectSerializer,
    TicketSerializer, 
    UserSerializer, 
    TicketHistorySerializer
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

class ProjectsListAPIView(generics.ListAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        owned_projects = Project.objects.filter(owner=self.request.user)
        assigned_projects = self.request.user.project_set.all()
        return sorted(
            chain(owned_projects, assigned_projects),
            key=attrgetter('created')
            )

class OwnedProjectListAPIView(generics.ListAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)

# class TicketListAPIView(generics.ListAPIView):
#     serializer_class = TicketSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         return Ticket.objects.filter(project=Project.objects.get(slug=self.kwargs['projectslug']))

# use permission
@api_view(http_method_names=['GET'])
def ticket_list_by_status(request, projectslug):
    project = Project.objects.get(slug=projectslug)
    output = {}
    statuses = ['IB', 'EM', 'IP', 'TS', 'CO']
    for status in statuses:
        output[status] = TicketSerializer(Ticket.objects.filter(project=project, status=status), many=True).data
    
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

# class TeamUserListAPIView(generics.ListAPIView):
#     serializer_class = UserSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         project = Project.objects.get(slug=self.kwargs['projectslug'])
#         output = []
#         for user in project.users.all():
#             obj = { 'id': user.id, 'username': user.username, 'isAdmin': False }
#             if (user in project.users.all()):
#                 obj['isAdmin'] = True
#             output.append(obj.copy())
#         return output

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

class TicketUpdateAPIView(generics.UpdateAPIView):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

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
    return Response(TicketSerializer(ticket).data)

class TicketHistoryListAPIView(generics.ListAPIView):
    serializer_class = TicketHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TicketHistory.objects.filter(ticket_id=self.kwargs['pk'])