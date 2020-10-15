import json

import requests
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import path
from .models import MenuItem, RSSItem, Contact
from .task import update_contacts

admin.site.register(MenuItem)
admin.site.register(RSSItem)


@admin.register(Contact)
class HeroAdmin(admin.ModelAdmin):
    change_list_template = "admin/contact_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('update/', self.do_update),
        ]
        return my_urls + urls

    def do_update(self, request):
        update_contacts()
        self.message_user(request, "Kontakty boli aktualizované.")
        return HttpResponseRedirect("../")
