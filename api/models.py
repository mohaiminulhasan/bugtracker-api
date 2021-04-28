from django.db import models

from django.conf import settings

# Create your models here.
class Project(models.Model):
  created = models.DateTimeField(auto_now_add=True)
  owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
  title = models.CharField(max_length=255)

  def __str__(self):
    return self.title


class Ticket(models.Model):
  PRIORITY_CHOICES = [
    ('H', 'High'),
    ('M', 'Medium'),
    ('L', 'Low'),
  ]
  STATUS_CHOICES = [
    ('IB', 'Ice Box'),
    ('EM', 'Emergency'),
    ('IP', 'In Progress'),
    ('TS', 'Testing'),
    ('CO', 'Complete'),
  ]
  TICKET_TYPE_CHOICES = [
    ('B', 'Bugs/Errors'),
    ('F', 'Features'),
    ('C', 'Change Requests'),
  ]
  created = models.DateTimeField(auto_now_add=True)
  title = models.CharField(max_length=30)
  description = models.CharField(max_length=255)
  project = models.ForeignKey(Project, on_delete=models.CASCADE)
  developer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='assignedtickets', on_delete=models.CASCADE)
  submitter = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='submittedtickets', on_delete=models.CASCADE)
  priority = models.CharField(max_length=1, choices=PRIORITY_CHOICES, default='M')
  status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='IB')
  ticket_type = models.CharField(max_length=1, choices=TICKET_TYPE_CHOICES, default='B')

  def __str__(self):
    return self.title


class TicketComment(models.Model):
  created = models.DateTimeField(auto_now_add=True)
  ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
  body = models.CharField(max_length=255)
  author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

  def __str__(self):
    return "%s: %s" % (self.author, self.body)