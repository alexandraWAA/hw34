from django.contrib import admin

from habits.models import Habit


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ["id", "action", "user", "time", "is_pleasant", "is_public"]
    list_display_links = ["id", "action"]
    list_filter = ["is_pleasant", "is_public", "periodicity"]
    search_fields = ["action", "place", "user__email"]
