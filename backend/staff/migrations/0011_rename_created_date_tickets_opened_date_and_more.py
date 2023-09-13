# Generated by Django 4.2.5 on 2023-09-12 09:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0003_alter_accounts_date_created_alter_transactions_date'),
        ('staff', '0010_alter_tickets_closed_by_alter_tickets_created_by'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tickets',
            old_name='created_date',
            new_name='opened_date',
        ),
        migrations.RemoveField(
            model_name='tickets',
            name='created_by',
        ),
        migrations.AddField(
            model_name='tickets',
            name='opened_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='opened_by', to='customer.customer'),
        ),
    ]
