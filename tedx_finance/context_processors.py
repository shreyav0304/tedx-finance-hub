def user_groups(request):
    """
    Context processor to add user group information to all templates.
    Admins (staff users) automatically have treasurer access.
    """
    user_preferences = None
    user_theme = None
    if request.user.is_authenticated:
        # Admins (staff users) get automatic treasurer access
        is_treasurer = request.user.is_staff or request.user.groups.filter(name='Treasurer').exists()

        # Attach or create preferences for theme/notifications
        try:
            from .models import UserPreference
            user_preferences, _ = UserPreference.objects.get_or_create(user=request.user)
            user_theme = user_preferences.theme
        except Exception:
            user_preferences = None
            user_theme = None
    else:
        is_treasurer = False
        user_preferences = None
        user_theme = None
    
    return {
        'is_treasurer': is_treasurer,
        'user_preferences': user_preferences,
        'user_theme': user_theme,
    }
