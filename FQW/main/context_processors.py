def notifications(request):
    if request.user.is_authenticated:
        return {'notifications': request.user.notifications.all()}
    return {}