# Generated by Django 5.0.6 on 2024-08-17 16:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0011_unit'),
    ]

    operations = [
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('quantity', models.IntegerField(null=True)),
                ('purchase_date', models.DateTimeField()),
                ('bank', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.bank')),
            ],
        ),
    ]
