from django.urls import path

from . import views

urlpatterns = [
  path('api-token-auth/', views.CustomAuthToken.as_view()),

  path('projects/', views.ProjectsListAPIView.as_view()),
  path('tickets/<slug:projectslug>/', views.TicketListAPIView.as_view()),
  path('users/<slug:projectslug>/', views.SingleUserListAPIView.as_view()),
  path('teamusers/<slug:projectslug>/', views.TeamUserListAPIView.as_view()),
]
