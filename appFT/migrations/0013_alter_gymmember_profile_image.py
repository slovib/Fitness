# Generated by Django 5.0.2 on 2024-10-25 19:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appFT', '0012_alter_gymmember_profile_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gymmember',
            name='profile_image',
            field=models.ImageField(default='default_avatar.jpeg', upload_to='media'),
        ),
    ]
