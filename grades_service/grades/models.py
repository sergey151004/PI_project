from django.db import models

class Grade(models.Model):
    student_id = models.IntegerField()  # ID из Users Service
    course_id = models.IntegerField()   # ID из Courses Service
    grade = models.CharField(max_length=2)  # A, B, C и т.д.