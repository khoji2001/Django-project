from django.contrib import admin
from .models import *

class MessageTextAdmin(admin.ModelAdmin):
    list_display = ('__str__','stat',)
    def stat(self, obj):
        return obj.status
    stat.boolean = True
    stat.short_description = 'حالت ارسال پیامک '
    
admin.site.register(MessageText,MessageTextAdmin)
admin.site.register(Emails)
