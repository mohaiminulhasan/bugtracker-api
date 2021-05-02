from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import Ticket, TicketHistory, Project

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
  if created:
    Token.objects.create(user=instance)

@receiver(pre_save, sender=Ticket)
def log_history(sender, instance, **kwargs):
  try:
    old = Ticket.objects.get(id=instance.id)
  except Ticket.DoesNotExist:
    return None
  for prop in ['title', 'description', 'project', 'developer', 'submitter', 'priority', 'status', 'ticket_type']:
    old_value = getattr(old, prop)
    new_value = getattr(instance, prop)
    if (old_value != new_value):
      TicketHistory.objects.create(ticket=instance, field=prop, old_value=old_value, new_value=new_value)

@receiver(post_save, sender=Project)
def remove_owner_from_project_users(sender, instance=None, **kwargs):
  user = instance.owner
  team = instance.users.all()
  if (user in team):
    team.remove(user)
