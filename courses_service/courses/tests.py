from django.test import TestCase

from django.test import TestCase
from rest_framework.test import APIClient

from .models import Course
from .serializers import CourseSerializer


class CourseModelTest(TestCase):

    def test_create_course(self):
        course = Course.objects.create(
            name="Math",
            description="Math course"
        )

        self.assertEqual(course.name, "Math")
        self.assertEqual(course.description, "Math course")


class CourseSerializerTest(TestCase):

    def test_course_serializer(self):
        course = Course.objects.create(
            name="Physics",
            description="Physics course"
        )

        serializer = CourseSerializer(course)
        data = serializer.data

        self.assertEqual(data["name"], "Physics")
        self.assertEqual(data["description"], "Physics course")


