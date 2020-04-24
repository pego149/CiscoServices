from django.db import models


class MenuItem(models.Model):
    name = models.CharField(max_length=200)

    def publish(self):
        self.save()

    def __str__(self):
        return self.name


class RSSItem(models.Model):
    name = models.CharField(max_length=200)
    url = models.CharField(max_length=200)

    def publish(self):
        self.save()

    def __str__(self):
        return self.name
