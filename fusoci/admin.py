from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from fusoci.models import * 

# Define an inline admin descriptor for UserProfile model
# which acts a bit like a singleton
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'profile'

# Define a new User admin
class UserAdmin(UserAdmin):
    inlines = (UserProfileInline, )

class BarCashBalanceAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'cashier':
            kwargs['queryset'] = UserProfile.objects.filter(user__is_staff=True)
        return super(BarCashBalanceAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

class EntranceCashBalanceAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'cashier':
            kwargs['queryset'] = UserProfile.objects.filter(user__is_staff=True)
        return super(EntranceCashBalanceAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Card)
admin.site.register(PurchasedProduct)
admin.site.register(Product)
admin.site.register(Receipt)
admin.site.register(Greeting)
admin.site.register(BarCashBalance, BarCashBalanceAdmin)
admin.site.register(EntranceCashBalance, EntranceCashBalanceAdmin)
admin.site.register(Entrance)
