"""
My template context processors
"""

def get_current_path(request):
    """
    Returns the full current path of the request
    """
    return {
        'current_path': request.get_full_path()
    }
