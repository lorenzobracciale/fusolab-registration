from django.contrib import admin
from cancello.models import *

# class GatePermissionAdmin(admin.ModelAdmin):
#     search_fields = ['user__username',]
# 
# admin.site.register(GatePermission,GatePermissionAdmin)
admin.site.register(GatePermission)
