from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Класс настройки админки пользователей."""
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'password'
    )
    list_filter = ('email', 'username')
    ordering = ('username', 'id',)
