"""
Render the about page
"""

from django.shortcuts import render

def index(request):
    """
    Render the hypermeet page
    """
    return render(request, 'hypermeet/index.html')
