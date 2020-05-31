# Generated by Django 3.0.6 on 2020-05-30 23:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0003_auto_20200530_0105'),
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('feedback', models.CharField(max_length=255, null=True)),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customers.Cart')),
            ],
        ),
    ]