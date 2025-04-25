from django.contrib import admin
from . models import UserProfile, Comuna, Address,Ciudad


# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Ciudad)
admin.site.register(Comuna)
admin.site.register(Address)
