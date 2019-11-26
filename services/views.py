from django.shortcuts import render
from .models import MenuItem


def services_list(request):
    items = MenuItem.objects.all()
    return render(request, 'services/services_list.xml', {'services': items}, content_type="application/xml")
