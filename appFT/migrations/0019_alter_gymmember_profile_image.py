# Generated by Django 5.0.2 on 2024-10-25 21:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appFT', '0018_trainingsession_plan'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gymmember',
            name='profile_image',
            field=models.ImageField(default='default_avatar.png', upload_to='profile_images'),
        ),
    ]
