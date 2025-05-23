from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from .models import UserProfile, Address
from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm, UserForm, ChangePasswordForm, AddressForm
from django.contrib import messages

# Create your views here.
@login_required(login_url='login')
def Profile(request):
    profile = UserProfile.objects.get(user=request.user)
    addresses = Address.objects.filter(user=request.user)

    return render(request, 'perfil.html' ,{
        'profile' : profile,
        'addresses' :addresses,
    })

@login_required(login_url='login')
def edit_profile(request):
    user_form = UserForm(instance=request.user)
    profile_form = UserProfileForm(instance=request.user.userprofile)
    
    if request.user.userprofile.address:
        address_form = AddressForm(instance=request.user.userprofile.address)
    else:
        address_form = AddressForm()

    next_url = request.GET.get('next') or request.POST.get('next')

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, instance=request.user.userprofile)
        address_form = AddressForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid() and address_form.is_valid():
            user_form.save()
            profile_form.save()

            if request.user.userprofile.address:
                request.user.userprofile.address.delete()

            address = address_form.save(commit=False)
            address.user = request.user 
            address.save() 

            request.user.userprofile.address = address
            request.user.userprofile.save()

            
            messages.success(request, "Perfil actualizado correctamente")

            if next_url:
                return redirect(next_url)
            return redirect('perfil')  
        

    return render(request, 'editar_perfil.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'address_form': address_form,
        'next': next_url
    })

@login_required(login_url='login')
def change_password(request):
    form = ChangePasswordForm(request.POST or None)

    form.user = request.user  
    user = request.user

    if request.method == 'POST' and form.is_valid():
        current_password = form.cleaned_data['current_password']
        new_password = form.cleaned_data['new_password']
        
        if not user.check_password(current_password):
            form.add_error('current_password', 'La contraseña actual es incorrecta.')
        elif user.check_password(new_password):
            form.add_error('new_password', 'La nueva contraseña debe ser diferente a la contraseña actual.')
        else:
            user.set_password(new_password)  
            user.save()  

            messages.success(request, "Contraseña cambiada exitosamente")
            return redirect('login') 

    return render(request, 'changed_password.html', {'form': form})
