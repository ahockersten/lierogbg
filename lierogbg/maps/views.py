"""
Default map view
"""

from django.shortcuts import render

def index(request):
    """
    Renders the default maps view
    """
    return render(request, 'maps/index.html')
