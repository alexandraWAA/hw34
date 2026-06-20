from django.contrib import admin

from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["id", "email", "first_name", "last_name", "is_active"]
    list_display_links = ["id", "email"]
    search_fields = ["email", "first_name", "last_name"]
    list_filter = ["is_active", "is_staff"]
