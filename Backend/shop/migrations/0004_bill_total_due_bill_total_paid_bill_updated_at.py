# Generated by Django 5.0.6 on 2024-08-04 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0003_bill_discount_bill_total_cost_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='bill',
            name='total_due',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='bill',
            name='total_paid',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='bill',
            name='updated_at',
            field=models.DateField(auto_now=True),
        ),
    ]
