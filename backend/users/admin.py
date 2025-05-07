from django.contrib import admin
from .models import CustomUser


class CustomUserAdmin(admin.ModelAdmin):
    # Указываем, какие поля будут отображаться в списке пользователей
    list_display = ("username", "email", "first_name", "last_name",
                    "date_joined")

    # Указываем, по каким полям можно будет производить поиск
    search_fields = ("username", "email")


# Регистрируем модель с кастомным администратором
admin.site.register(CustomUser, CustomUserAdmin)
