import json
import requests

from .models import Contact
from .views import UTFToASCII


def update_contacts():
    Contact.objects.all().delete()
    for i in 'abcdefghijklmnopqrstuvwxyz':
        url = "http://nic.uniza.sk/webservices/getDirectory.php?q=" + i
        req = requests.get(url)
        req.encoding = 'win-1250'
        jsonData = json.loads(req.content.decode())
        jsonList = jsonData['directory']
        for dir in jsonList:
            contact = Contact(oc=dir['oc'], function=dir['function'], name=UTFToASCII(dir['name']),
                              tel=dir['tel'].replace(" ", ""), mobil=dir['mobil'].replace(" ", ""),
                              mail=dir['mail'], job=dir['job'], room=dir['room'])
            try:
                exist = Contact.objects.get(oc=dir['oc'])
            except Contact.DoesNotExist:
                exist = None
            if exist is None:
                contact.save()