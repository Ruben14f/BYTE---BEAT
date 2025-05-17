from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def assign_group_based_on_user_type(sender, instance, created, **kwargs):
    if created:
        if instance.is_superuser:
            group, _ = Group.objects.get_or_create(name='Admins')
        else:
            group, _ = Group.objects.get_or_create(name='Clientes')
        instance.groups.add(group)
