from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from users.models import User
from habits.models import Habit


class HabitTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.habit_data = {
            'place': 'Home',
            'time': '08:00:00',
            'action': 'Exercise',
            'execution_time': 60,
            'periodicity': 1
        }

    def test_create_habit_success(self):
        url = reverse('habit-list-create')
        response = self.client.post(url, self.habit_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), 1)

    def test_create_habit_invalid_execution_time(self):
        data = self.habit_data.copy()
        data['execution_time'] = 150
        url = reverse('habit-list-create')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_user_habits(self):
        Habit.objects.create(user=self.user, **self.habit_data)
        url = reverse('habit-list-create')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_public_habits_list(self):
        # Создаем публичную привычку
        Habit.objects.create(
            user=self.user,
            is_public=True,
            **self.habit_data
        )
        url = reverse('public-habits')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)