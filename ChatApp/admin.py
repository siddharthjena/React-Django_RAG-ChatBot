from django.contrib import admin
from .models import Chat

# Register the Employee model to make it accessible in the admin interface
admin.site.register(Chat)