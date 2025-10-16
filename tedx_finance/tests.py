from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class AuthFlowTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username="tester", password="pass1234")

	def test_login_and_logout_post(self):
		# Login
		resp = self.client.post(reverse("login"), {"username": "tester", "password": "pass1234"})
		self.assertEqual(resp.status_code, 302)  # redirect after login

		# Logout via POST
		resp = self.client.post(reverse("logout"))
		self.assertIn(resp.status_code, [302, 303])
		# After logout, accessing dashboard should redirect to login
		resp = self.client.get(reverse("tedx_finance:dashboard"))
		self.assertIn(resp.status_code, [302, 303])
