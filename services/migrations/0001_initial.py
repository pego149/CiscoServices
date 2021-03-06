# Generated by Django 3.1.2 on 2020-10-15 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('oc', models.IntegerField()),
                ('function', models.CharField(blank=True, max_length=200, null=True)),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
                ('tel', models.CharField(blank=True, max_length=200, null=True)),
                ('mobil', models.CharField(blank=True, max_length=200, null=True)),
                ('mail', models.CharField(blank=True, max_length=200, null=True)),
                ('job', models.CharField(blank=True, max_length=200, null=True)),
                ('room', models.CharField(blank=True, max_length=200, null=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='MenuItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='RSSItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('url', models.CharField(max_length=200)),
            ],
        ),
    ]
