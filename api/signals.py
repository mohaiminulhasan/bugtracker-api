import json
from django.conf import settings
from django.db.models.signals import pre_delete, post_save, pre_save
from django.dispatch import receiver
from django.utils.text import slugify

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import Ticket, TicketHistory, Project, TicketOrder

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
    if old_value is None:
      old_value = ''
    new_value = getattr(instance, prop)
    if new_value is None:
      new_value = ''
    if (old_value != new_value):
      TicketHistory.objects.create(ticket=instance, field=prop, old_value=old_value, new_value=new_value)

@receiver(post_save, sender=Project)
def remove_owner_from_project_users(sender, instance=None, **kwargs):
  if not instance.slug:
    instance.slug = slugify(instance.title)
    instance.save()
  user = instance.owner
  team = instance.users.all()
  if (user in team):
    team.remove(user)

@receiver(pre_delete, sender=Ticket)
def remove_ticket_id_from_ticket_order(sender, instance, **kwargs):
  objs = TicketOrder.objects.filter(project=instance.project)
  for obj in objs:
    tickets = json.loads(obj.tickets)
    if instance.id in tickets:
      tickets.remove(instance.id)
      obj.tickets = json.dumps(tickets)
      obj.save()
      