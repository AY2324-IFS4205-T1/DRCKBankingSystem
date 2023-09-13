# Generated by Django 4.2.5 on 2023-09-13 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0003_alter_transactions_recipient_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='transactions',
            name='transaction_type',
            field=models.CharField(choices=[('D', 'Deposit'), ('W', 'Withdrawal'), ('T', 'Transfer')], default='D', max_length=1),
            preserve_default=False,
        ),
    ]