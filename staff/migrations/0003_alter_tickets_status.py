# Generated by Django 4.2.5 on 2023-09-13 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tickets',
            name='status',
            field=models.CharField(choices=[('O', 'Open'), ('A', 'Approved'), ('R', 'Rejected')], max_length=1),
        ),
    ]