def user_groups(request):
    """
    Context processor to add user group information to all templates.
    """
    if request.user.is_authenticated:
        is_treasurer = request.user.groups.filter(name='Treasurer').exists()
    else:
        is_treasurer = False
    
    return {
        'is_treasurer': is_treasurer,
    }
