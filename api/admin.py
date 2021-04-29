from django.contrib import admin

from .models import Project, Ticket, TicketComment, TicketHistory

# Register your models here.
class ProjectAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
admin.site.register(Project, ProjectAdmin)
admin.site.register(Ticket)
admin.site.register(TicketComment)

class TicketHistoryAdmin(admin.ModelAdmin):
  list_display = ('ticket', 'field', 'old_value', 'new_value', 'created')
admin.site.register(TicketHistory, TicketHistoryAdmin)