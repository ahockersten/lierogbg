##
# @file views.py
#

from django.shortcuts import render
from django.shortcuts import redirect
from django.template import Context

from django.contrib import auth
from django.utils.translation import ugettext_lazy as _

##
# try to authenticate
#
def authenticate(request):
    username = request.POST['username']
    password = request.POST['password']

    user = auth.authenticate(username=username, password=password)

    if user is not None:
        if user.is_active:
            auth.login(request, user)
            return redirect('index.views.ranking')
        else:
            context = Context({
                'error_msg' : _('User disabled')
            })

            return render(request, 'accounts/error.html', context)
    else:
        context = Context({
            'error_msg' : _('User does not exist')
        })
        return render(request, 'accounts/error.html', context)

##
# main login screen
#
def login(request):
    if request.GET.get('next'):
        next_view = request.GET['next']
    else:
        next_view = 'index.views.ranking'

    context = Context()

    if request.user.is_authenticated():
        return redirect(next_view)
    else:
        return render(request, 'accounts/login.html', context)

##
# logout screen
#
def logout(request):
    if request.user.is_authenticated():
        # Logout
        auth.logout(request)

    return redirect('index.views.ranking')

