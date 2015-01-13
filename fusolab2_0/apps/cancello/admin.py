from django.contrib import admin
from django.contrib.auth.models import User
from cancello.models import *
from base.models import UserProfile

class GatePermissionAdmin(admin.ModelAdmin):
   search_fields = ['user__username',]
   #ordering = ('user__username',)
   def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            #kwargs["queryset"] = User.objects.filter(groups__name='turnisti')
            kwargs["queryset"] = UserProfile.objects.filter(user__groups__name='turnisti')
        return super(GatePermissionAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
# 
admin.site.register(GatePermission,GatePermissionAdmin)
#admin.site.register(GatePermission)
