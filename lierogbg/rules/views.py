"""
Rules view
"""

from django.shortcuts import render

def index(request):
    return render(request, 'rules/index.html')
