from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from ingresso.models import * 

class EntranceBalanceAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'cashier':
            kwargs['queryset'] = UserProfile.objects.filter(user__is_staff=True)
        return super(EntranceBalanceAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

# Re-register UserAdmin
admin.site.register(Card)
admin.site.register(EntranceBalance, EntranceBalanceAdmin)
admin.site.register(Entrance)