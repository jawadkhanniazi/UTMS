# Generated by Django 4.2 on 2025-01-11 06:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Owners',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ownerCnic', models.CharField(max_length=50)),
                ('ownerName', models.CharField(max_length=50)),
                ('ownerAddress', models.TextField()),
                ('ownerEmail', models.EmailField(blank=True, max_length=254, null=True)),
                ('ownerPostalAddress', models.TextField()),
                ('ownerPhone', models.CharField(max_length=50)),
                ('ownerWhatsapp', models.CharField(max_length=50)),
                ('ownerNextOfKin', models.CharField(max_length=50)),
                ('ownerNextOfKinPhone', models.CharField(max_length=50)),
                ('ownerNextOfKinWhatsapp', models.CharField(max_length=50)),
                ('ownerNextOfKinAddress', models.TextField()),
                ('ownerNextOfKinPostalAddress', models.TextField()),
                ('ownerNextOfKinEmail', models.EmailField(blank=True, max_length=254, null=True)),
                ('ownerNextOfKinCnic', models.CharField(max_length=50)),
                ('ownerNextOfKinRelation', models.CharField(max_length=50)),
            ],
        ),
    ]
