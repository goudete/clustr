# Generated by Django 3.0.6 on 2020-06-24 19:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='cash_code',
            field=models.CharField(default=None, max_length=255, null=True),
        ),
    ]