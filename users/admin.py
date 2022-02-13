from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from .forms import UserCreationForm, UserChangeForm
from .models import User
# from rest_framework.authtoken.models import TokenProxy
 
class UserAdmin(UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm 
    model = User
    exclude = ('username',)
    list_display = ('__str__','mobile_number', 'is_active',)
    list_filter = ( 'is_staff', 'is_active',)
    search_fields = ('mobile_number', 'first_name','last_name','melli_code')
    ordering = ('date_joined',)
    fieldsets = (
        (None, {'classes': ('wide',),
            'fields': ('mobile_number', 'password',)}),
        ('اطلاعات شخصی',{'fields': ( 'first_name' ,'last_name' ,'father_name','gender','melli_code','email','education','phone_number', 'phone_number_description', 'workplace_number', 'description' ) } ),
        ('اطلاعات سکونتی',{'fields': ( 'province' ,'city', 'address', ) } ),
        ('دسترسی ها', {'fields': ('is_staff', 'is_active', 'is_superuser', 'user_permissions', 'groups', ) } ),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('mobile_number', 'password1', 'password2')}
        ),
        ('اطلاعات شخصی',{'fields': ( 'first_name' ,'last_name' ,'father_name', 'gender','melli_code','email' , 'phone_number' , 'workplace_number')}),
        ('اطلاعات سکونتی',{'fields': ( 'province' ,'city', 'address',)}),
        ('دسترسی ها', {'fields': ('is_staff', 'is_active', 'is_superuser', 'user_permissions', 'groups',)}),
    )


admin.site.register(User,UserAdmin)
# admin.site.unregister(Group)
# admin.site.unregister(TokenProxy)
