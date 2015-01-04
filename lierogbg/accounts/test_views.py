# vim: set fileencoding=utf-8 ts=4 sw=4 expandtab fdm=marker:
# pylint: disable=too-many-public-methods

"""
Tests for the accounts app - views.
"""

from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.models import User, AnonymousUser
from django.http import QueryDict
from django.test import Client, TestCase, RequestFactory

from accounts.views import authenticate, login, logout

def add_session_to_request(request):
    """
    Annotate a request object with a session
    """
    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()

class ViewTest(TestCase):
    """
    Tests for Accounting - Views.
    """
    def setUp(self):
        """
        Setup before each tests. A request factory and a valid user.
        """
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='jacob', email='jacob@example.com',
            password='top_secret')

    def test_login_no_user(self):
        """
        Test logging in without a valid user.
        """
        # Create an instance of a GET request.
        request = self.factory.get('/accounts/login')

        request.user = AnonymousUser()

        # Test the login view as if it was deployed as 'accounts/login'
        response = login(request)
        self.assertEqual(response.status_code, 200)

    def test_login_with_user(self):
        """
        Test logging in with a valid user.
        """
        # Create an instance of a GET request.
        request = self.factory.get('/accounts/login')

        request.user = self.user

        # Should get a redirect
        response = login(request)
        self.assertEqual(response.status_code, 302)

    def test_login_with_user_redirect(self):
        """
        Test logging in with a redirect
        """
        # Create an instance of a GET request.
        request = self.factory.get('/accounts/login')

        request.user = self.user
        request.GET = QueryDict('next=/')

        # Should get a redirect
        response = login(request)
        self.assertEqual(response.status_code, 302)

    def test_logout_with_user(self):
        """
        Test logging out with a valid user.
        """
        # Create an instance of a GET request.
        request = self.factory.get('/accounts/logout')

        request.user = self.user
        add_session_to_request(request)

        # Should get a redirect
        response = logout(request)
        self.assertEqual(response.status_code, 302)

    def test_auth_with_invalid_post(self):
        """
        Test authentication with an invalid POST request.
        """
        # Create an instance of a POST request.
        request = self.factory.post('/accounts/authenticate')

        # don't fill it up with username/password info

        # Should get a redirect
        response = authenticate(request)
        self.assertEqual(response.status_code, 200)

    def test_auth_with_valid_post(self):
        """
        Test authentication with a valid POST request, but not a valid user
        """
        # Create an instance of a POST request.
        request = self.factory.post('/accounts/authenticate')

        request.POST['username'] = 'Joe'
        request.POST['password'] = 'Schmoe'

        # Should get a redirect
        response = authenticate(request)
        self.assertEqual(response.status_code, 200)

    def test_auth_with_valid_user(self):
        """
        Test authentication with a valid POST request, but not a valid user
        """
        # Create an instance of a POST request.
        request = self.factory.post('/accounts/authenticate')

        #
        # Clever hack: To get a valid session, we can use the client() class
        # to generate a session dictionary and pass that with the request
        # when authenticating
        #
        client = Client()
        client.login(username='jacob', password='top_secret')
        request.session = client.session

        request.POST['username'] = 'jacob'
        request.POST['password'] = 'top_secret'

        # Should get a redirect
        response = authenticate(request)
        self.assertEqual(response.status_code, 302)

    def test_auth_with_inactive_user(self):
        """
        Test authentication with a valid POST request and a valid user, but
        an inactivated user...
        """
        # Create an instance of a POST request.
        request = self.factory.post('/accounts/authenticate')

        # Create an inactive user
        user = User.objects.create_user(
            username='foo', email='foo@bar.com',
            password='foo')
        user.is_active = False
        user.save()

        #
        # Clever hack: To get a valid session, we can use the client() class
        # to generate a session dictionary and pass that with the request
        # when authenticating
        #
        client = Client()
        client.login(username='foo', password='foo')
        request.session = self.client.session

        request.POST['username'] = 'foo'
        request.POST['password'] = 'foo'

        response = authenticate(request)
        self.assertEqual(response.status_code, 200)

    def test_auth_with_wrong_password(self):
        """
        Test authentication with a valid POST request and a valid user, but
        the wrong password
        """
        # Create an instance of a POST request.
        request = self.factory.post('/accounts/authenticate')

        # Create a user
        User.objects.create_user(
            username='foo', email='foo@bar.com',
            password='foo')

        #
        # Clever hack: To get a valid session, we can use the client() class
        # to generate a session dictionary and pass that with the request
        # when authenticating
        #
        client = Client()
        client.login(username='foo', password='foo')
        request.session = self.client.session

        request.POST['username'] = 'foo'
        request.POST['password'] = 'bar'

        response = authenticate(request)
        self.assertEqual(response.status_code, 200)
