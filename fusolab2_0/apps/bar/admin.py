from django.contrib import admin
from django import forms
from bar.models import * 

class BarBalanceAdmin(admin.ModelAdmin):
    ordering = ('-date',)
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'cashier':
            kwargs['queryset'] = UserProfile.objects.filter(user__groups__name='turnisti').order_by('user__first_name','user__last_name')
        return super(BarBalanceAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

class SmallBalanceAdmin(admin.ModelAdmin):
    ordering = ('-date',)
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'cashier':
            kwargs['queryset'] = UserProfile.objects.filter(user__groups__name='turnisti').order_by('user__first_name','user__last_name')
        return super(SmallBalanceAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


# Re-register UserAdmin
admin.site.register(PurchasedProduct)
admin.site.register(Product)
admin.site.register(Receipt)
admin.site.register(BarBalance, BarBalanceAdmin)
admin.site.register(SmallBalance, SmallBalanceAdmin)
