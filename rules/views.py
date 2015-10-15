"""
Rules view
"""
from django.shortcuts import render


def index(request):
    """
    Renders the rules.
    """
    return render(request, 'rules/index.html')
