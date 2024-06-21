from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _
from core import models


class UserAdmin(DjangoUserAdmin):
    ordering = ['id', 'username']
    list_display = ['username', 'email']
    fieldsets = (
        (None, {'fields': ('username', 'email', 'name', 'password')}),
        (
            _('Permissions'),
            {
                'fields': ('is_active', 'is_staff', 'is_superuser')
            }
        ),
        (_('Additional Information'), {'fields': ('last_login',)})
    )
    readonly_fields = ['last_login']
    add_fieldsets = (
        (None, {'fields': (
            'username',
            'email',
            'password1',
            'password2',
            'name',
            'is_active',
            'is_staff',
            'is_superuser'
        ), }),
    )


admin.site.register(models.User, UserAdmin)
