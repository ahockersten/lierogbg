"""
Render the about page
"""

from django.shortcuts import render

def index(request):
    """
    Render the about page
    """
    return render(request, 'about/index.html')
