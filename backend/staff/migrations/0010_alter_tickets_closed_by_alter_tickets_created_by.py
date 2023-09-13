# Generated by Django 4.2.5 on 2023-09-12 08:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0003_alter_accounts_date_created_alter_transactions_date'),
        ('staff', '0009_alter_tickets_created_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tickets',
            name='closed_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='closed_by', to='staff.staff'),
        ),
        migrations.AlterField(
            model_name='tickets',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='created_by', to='customer.customer'),
        ),
    ]
