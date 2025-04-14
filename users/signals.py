from django.contrib.auth.models import Group
from django.db.models.signals import post_migrate
from django.dispatch import receiver

@receiver(post_migrate)
def create_groups(sender, **kwargs):
    # Crear los grupos si no existen
    Group.objects.get_or_create(name='Clientes')
    Group.objects.get_or_create(name='Admins')