from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()

class ImpersonationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_group = Group.objects.create(name='Admin')
        self.admin_user = User.objects.create_superuser('admin', 'admin@test.com', 'password')
        self.admin_user.groups.add(self.admin_group)
        self.regular_user = User.objects.create_user('user', 'user@test.com', 'password')

    def test_impersonate_user(self):
        self.client.login(username='admin', password='password')
        response = self.client.get(reverse('accounts:impersonate-user', args=[self.regular_user.id]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'You are now impersonating {self.regular_user.username}')

    def test_stop_impersonating(self):
        self.client.login(username='admin', password='password')
        self.client.get(reverse('accounts:impersonate-user', args=[self.regular_user.id]))
        response = self.client.get(reverse('accounts:stop-impersonating'))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('impersonating_id', self.client.session)