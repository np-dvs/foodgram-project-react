from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class MyUserAdmin(UserAdmin):

    list_display = ('email', 'first_name',
                    'last_name',)
    list_filter = ('email', 'first_name')
