# vim: set fileencoding=utf-8 ts=4 sw=4 expandtab fdm=marker:
# pylint: disable=too-many-public-methods

"""
Tests for the about app views
"""

from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase, RequestFactory

from about.views import index


class TestView(TestCase):
    """
    Tests for About - Views.
    """
    def setUp(self):
        """
        Setup before each test. A request factory and a valid user.
        """
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='jacob', email='jacob@example.com',
            password='top_secret')

    def test_index(self):
        """
        Test index. Does not require a valid user
        """
        # Create an instance of a GET request.
        request = self.factory.get('/accounts/login')

        request.user = AnonymousUser()

        response = index(request)
        self.assertEqual(response.status_code, 200)
