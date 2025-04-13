def user_initial(request):
    if request.user.is_authenticated:
        # Obtener la inicial del nombre del usuario
        initial = request.user.first_name[0] if request.user.first_name else request.user.username[0]
    else:
        initial = ''
    return {'initial': initial}