from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')

    search_fields = ('username', 'first_name', 'email')

    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields' : ('username', 'password')}),
        ('Personal Info', {'fields' : ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields' : ('is_active', 'is_superuser', 'is_staff', 'groups', 'uesr_permissions')}),
        ('Important Dates', {'fields' : ('last_login', 'date_joined')}),
     )
    add_fieldsets = (
        (None, {
            'classes' : ('wide',),
            'fields' : ('username', 'email', 'password1', 'password2', 'bio'),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)