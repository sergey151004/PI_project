from django.test import TestCase
from rest_framework.test import APIClient
from .models import Grade
from .serializers import GradeSerializer


class GradeModelTest(TestCase):

    def test_create_grade(self):
        grade = Grade.objects.create(
            student_id=1,
            course_id=10,
            grade="A"
        )

        self.assertEqual(grade.student_id, 1)
        self.assertEqual(grade.course_id, 10)
        self.assertEqual(grade.grade, "A")


class GradeSerializerTest(TestCase):

    def test_grade_serializer(self):
        grade = Grade.objects.create(
            student_id=2,
            course_id=20,
            grade="B"
        )

        serializer = GradeSerializer(grade)
        data = serializer.data

        self.assertEqual(data["student_id"], 2)
        self.assertEqual(data["course_id"], 20)
        self.assertEqual(data["grade"], "B")


class GradeAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()

        Grade.objects.create(
            student_id=1,
            course_id=1,
            grade="A"
        )

    def test_get_grades(self):
        response = self.client.get("/api/grades/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_create_grade(self):
        data = {
            "student_id": 3,
            "course_id": 2,
            "grade": "C"
        }

        response = self.client.post("/api/grades/", data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Grade.objects.count(), 2)