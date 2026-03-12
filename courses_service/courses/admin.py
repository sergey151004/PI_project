from django.contrib import admin
from .models import Course

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    list_display_links = ('id', 'name')  # id и name кликабельные
    search_fields = ('name', 'description')
    ordering = ('-id',)  # новые сверху