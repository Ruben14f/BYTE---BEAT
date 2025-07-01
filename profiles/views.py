from django.shortcuts import render, redirect
from .models import UserProfile, Address
from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm, UserForm, ChangePasswordForm, AddressForm
from django.contrib import messages

# Create your views here.
@login_required(login_url='login')
def Profile(request):
    profile = UserProfile.objects.select_related('user', 'address__comuna', 'address__ciudad').get(user=request.user)


    return render(request, 'perfil.html' ,{
        'profile' : profile,
        'addresses' :profile.address,
    })

@login_required(login_url='login')
def edit_profile(request):
    user = request.user
    user_profile = user.userprofile
    address_instance = user_profile.address  # Puede ser None

    next_url = request.GET.get('next') or request.POST.get('next')

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, instance=user_profile)
        address_form = AddressForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid() and address_form.is_valid():
            user_form.save()
            profile_form.save()

            # Reemplazar dirección anterior si existe
            if address_instance:
                address_instance.delete()

            new_address = address_form.save(commit=False)
            new_address.user = user
            new_address.save()

            user_profile.address = new_address
            user_profile.save()

            messages.success(request, "Perfil actualizado correctamente")
            return redirect(next_url or 'perfil')

    else:
        user_form = UserForm(instance=user)
        profile_form = UserProfileForm(instance=user_profile)
        address_form = AddressForm(instance=address_instance)

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
