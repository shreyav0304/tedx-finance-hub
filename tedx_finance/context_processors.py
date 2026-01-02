def user_groups(request):
    """
    Context processor to add user group information to all templates.
    Admins (staff users) automatically have treasurer access.
    """
    if request.user.is_authenticated:
        # Admins (staff users) get automatic treasurer access
        is_treasurer = request.user.is_staff or request.user.groups.filter(name='Treasurer').exists()
    else:
        is_treasurer = False
    
    return {
        'is_treasurer': is_treasurer,
    }
