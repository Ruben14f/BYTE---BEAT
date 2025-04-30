# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

class Comuna(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Ciudad(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    calle = models.CharField(max_length=225, blank=False, null=False)
    num_direccion = models.CharField(blank=False, null=False)
    comuna = models.ForeignKey(Comuna, on_delete=models.CASCADE, blank=False, null=False)
    ciudad = models.ForeignKey(Ciudad, on_delete=models.CASCADE, blank=False, null=False)

    def __str__(self):
        return f"{self.calle}, {self.num_direccion}, {self.ciudad}, {self.comuna.name}"

    def full_address(self):
        return f"{self.direccion}, {self.ciudad}, {self.comuna.name}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} profile"
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)  

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()  