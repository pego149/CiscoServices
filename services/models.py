from django.db import models


class MenuItem(models.Model):
    """
    Model predstavuje služby podporované naším systémom, ktoré sa zobrazia
    v hlavnom menu IP telefónu. Služby je možné pridávať prostredníctvom administrátorského
    panelu implementovaného vo frameworku Django. V databáze uchovávame jediný atribút
    a to názov služby, z ktorého je potom odvodená url adresa danej služby.
    :param models.Model: podtrieda django.db.models.Model
    """
    name = models.CharField(max_length=200)

    def publish(self):
        self.save()

    def __str__(self):
        return self.name


class RSSItem(models.Model):
    """
    Model predstavuje poskytovateľov od ktorých sú prijímané RSS správy. Aj
    poskytovateľov je možné pridávať pomocou administrátorského panelu. V databáze
    uchovávame meno poskytovateľa a URL adresu, na ktorej sa nachádza zdroj RSS správ.
    :param models.Model: podtrieda django.db.models.Model
    """
    name = models.CharField(max_length=200)
    url = models.CharField(max_length=200)

    def publish(self):
        self.save()

    def __str__(self):
        return self.name


class Contact(models.Model):
    """
    Model
    :param models.Model: podtrieda django.db.models.Model
    """
    oc = models.IntegerField()
    function = models.CharField(max_length=200, null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    tel = models.CharField(max_length=200, null=True, blank=True)
    mobil = models.CharField(max_length=200, null=True, blank=True)
    mail = models.CharField(max_length=200, null=True, blank=True)
    job = models.CharField(max_length=200, null=True, blank=True)
    room = models.CharField(max_length=200, null=True, blank=True)

    def publish(self):
        self.save()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']