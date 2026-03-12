from django.contrib import admin
from .models import Grade


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('id', 'student_id', 'course_id', 'grade',)
    list_display_links = ('id',)  # только id кликабельный (можно добавить student_id, course_id)
    list_filter = ('grade',)
    search_fields = ('student_id', 'course_id')
    ordering = ('-id',)  # новые сверху

    # если есть поле date, можно добавить:
    # list_filter = (('date', DateFieldListFilter), 'grade')