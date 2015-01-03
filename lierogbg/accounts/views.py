"""
Views for the accounts app. These views handle login, logout and
authentication.
"""

from django.shortcuts import render
from django.shortcuts import redirect

from django.contrib import auth
from django.utils.translation import ugettext_lazy as _

def authenticate(request):
    """
    This view will perform the actual authentication of a user.

    :param request: The HTTP request
    :type request: HttpRequest
    :returns: A HttpResponse
    """
    username = request.POST['username']
    password = request.POST['password']

    user = auth.authenticate(username=username, password=password)

    if user is not None:
        if user.is_active:
            auth.login(request, user)
            return redirect('rankings.views.ranking')
        else:
            context = {
                'error_msg' : _('User disabled')
            }

            return render(request, 'accounts/error.html', context)
    else:
        context = {
            'error_msg' : _('User does not exist')
        }
        return render(request, 'accounts/error.html', context)

def login(request):
    """
    The login-view. Displays the actual login-screen.

    :param request: The HTTP request
    :type request: HttpRequest
    :returns: A HttpResponse
    """
    if request.GET.get('next'):
        next_view = request.GET['next']
    else:
        next_view = 'rankings.views.ranking'

    if request.user.is_authenticated():
        return redirect(next_view)
    else:
        return render(request, 'accounts/login.html')

def logout(request):
    """
    The logout-view. Will always re-direct to the login screen, and
    perhaps logout the user from the auth system.

    :param request: The HTTP request
    :type request: HttpRequest
    :returns: A HttpResponse
    """
    if request.user.is_authenticated():
        # Logout
        auth.logout(request)

    return redirect('rankings.views.ranking')

