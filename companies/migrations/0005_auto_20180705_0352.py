# Generated by Django 2.0.6 on 2018-07-05 03:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0004_auto_20170821_2000'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='slug',
            field=models.SlugField(max_length=200, unique=True),
        ),
    ]
