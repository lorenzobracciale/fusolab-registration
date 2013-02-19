from django.contrib import admin

from bar.models import * 

class BarBalanceAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'cashier':
            kwargs['queryset'] = UserProfile.objects.filter(user__is_staff=True)
        return super(BarBalanceAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

# Re-register UserAdmin
admin.site.register(PurchasedProduct)
admin.site.register(Product)
admin.site.register(Receipt)
admin.site.register(BarBalance, BarBalanceAdmin)