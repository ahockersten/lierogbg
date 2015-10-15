"""
Views for the customer app
"""

from django.shortcuts import render

def index(request):
    """
    Simple renderer for the actual app.

    :param request: The HTTP Request
    :type request: HTTPRequest
    :returns: A HTTP Response
    """
    return render(request, 'index/index.html')
