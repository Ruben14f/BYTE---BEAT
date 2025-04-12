from django.shortcuts import render

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        initial = request.user.first_name[0] if request.user.first_name else ''
    else:
        initial = ''
    return render(request, 'index.html',{'initial': initial})
