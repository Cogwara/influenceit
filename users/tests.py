
from django.test import TestCase
from .models import User

class UserModelTest(TestCase):
    def test_user_creation(self):
        user = User.objects.create_user(username='testuser', password='testpass')
        self.assertEqual(user.username, 'testuser')