from django.urls import path

from . import views

urlpatterns = [
  path('api-token-auth/', views.CustomAuthToken.as_view()),

  path('projects/', views.ProjectsListAPIView.as_view()),
  path('tickets/', views.TicketListAPIView.as_view()),
]
