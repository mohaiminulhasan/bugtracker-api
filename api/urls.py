from django.urls import path

from . import views

urlpatterns = [
  path('api-token-auth/', views.CustomAuthToken.as_view()),
  path('projects/', views.ProjectsListAPIView.as_view()),
  path('owned/projects/', views.OwnedProjectListAPIView.as_view()),
  path('tickets/in/<slug:projectslug>/', views.ticket_list_by_status),
  path('users/<slug:projectslug>/', views.SingleUserListAPIView.as_view()),
  path('teamusers/<slug:projectslug>/', views.team_user_list),
  path('add/<str:username>/to/team/<slug:projectslug>/', views.add_to_team),
  path('remove/<str:username>/from/team/<slug:projectslug>/', views.remove_from_team),
  path('toggle/<str:username>/to/<slug:projectslug>/as/admin/', views.toggle_as_admin),
  path('move/<int:pk>/', views.TicketUpdateAPIView.as_view()),
  path('tickets/<int:pk>/', views.TicketRetrieveAPIView.as_view()),
  path('tickets/create/', views.create_ticket),
  path('tickets/<int:pk>/history/', views.TicketHistoryListAPIView.as_view()),
  path('tickets/<int:pk>/comments/', views.TicketCommentListAPIView.as_view()),
]
