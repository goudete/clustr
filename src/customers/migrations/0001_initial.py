# Generated by Django 3.0.6 on 2020-09-08 08:10

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('restaurant_admin', '0001_initial'),
        ('cashier', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_paid', models.BooleanField(default=False)),
                ('is_entered', models.BooleanField(default=False)),
                ('shipping_cost', models.DecimalField(decimal_places=2, default=0, max_digits=12, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('shipping_cost_stored', models.BooleanField(default=False)),
                ('total', models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('stripe_order_id', models.CharField(max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('paid_at', models.DateTimeField(null=True)),
                ('email', models.EmailField(max_length=200)),
                ('receipt_html', models.TextField(null=True)),
                ('is_cancelled', models.BooleanField(default=False)),
                ('cash_payment', models.BooleanField(null=True)),
                ('first_name', models.CharField(max_length=255, null=True)),
                ('last_name', models.CharField(max_length=255, null=True)),
                ('handle_cash', models.BooleanField(null=True)),
                ('cashier', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cashier.CashierProfile')),
                ('restaurant', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='restaurant_admin.Restaurant')),
            ],
        ),
        migrations.CreateModel(
            name='OrderTracker',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_complete', models.BooleanField(default=False)),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customers.Cart')),
                ('restaurant', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='restaurant_admin.Restaurant')),
            ],
        ),
        migrations.CreateModel(
            name='ShippingInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=255, null=True)),
                ('email', models.EmailField(max_length=200)),
                ('tel', models.CharField(max_length=255, null=True)),
                ('address', models.CharField(max_length=255, null=True)),
                ('city_name', models.CharField(max_length=255, null=True)),
                ('city_id', models.CharField(max_length=255, null=True)),
                ('postcode', models.CharField(max_length=255, null=True)),
                ('order_tracker', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='customers.OrderTracker')),
            ],
        ),
        migrations.CreateModel(
            name='MenuItemCounter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('custom_instructions', models.CharField(blank=True, default=None, max_length=255, null=True)),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=12, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('addon_items', models.ManyToManyField(blank=True, to='restaurant_admin.AddOnItem')),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customers.Cart')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='restaurant_admin.MenuItem')),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='restaurant_admin.Restaurant')),
            ],
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('feedback', models.CharField(max_length=255, null=True)),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customers.Cart')),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripe_id', models.CharField(max_length=255, null=True)),
                ('shipping_info_stored', models.BooleanField(default=False)),
                ('card_stored', models.BooleanField(default=False)),
                ('shipping_info', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='customers.ShippingInfo')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='cart',
            name='shipping_info',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='customers.ShippingInfo'),
        ),
    ]
