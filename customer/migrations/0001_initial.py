# Generated by Django 4.2.5 on 2023-09-13 07:07

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Accounts',
            fields=[
                ('account', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('balance', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('status', models.CharField(choices=[('A', 'Active'), ('P', 'Pending'), ('C', 'Closed')], max_length=1)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'customer"."accounts',
            },
        ),
        migrations.CreateModel(
            name='AccountTypes',
            fields=[
                ('type', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'customer"."account_types',
            },
        ),
    ]