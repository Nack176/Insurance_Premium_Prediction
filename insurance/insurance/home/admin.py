from django.contrib import admin
from django.contrib.auth.models import User
from .models import ContactMessage, Prediction

class CustomAdminSite(admin.AdminSite):
    site_header = "Insurance Premium Prediction Admin"
    site_title = "Admin Portal"
    index_title = "Dashboard"

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        # Add dashboard data
        extra_context['total_predictions'] = Prediction.objects.count()
        extra_context['total_users'] = User.objects.count()
        extra_context['total_contact_messages'] = ContactMessage.objects.count()
        return super().index(request, extra_context)

custom_admin_site = CustomAdminSite(name='custom_admin')

# Register your models here.
custom_admin_site.register(User)
custom_admin_site.register(ContactMessage)
custom_admin_site.register(Prediction)
